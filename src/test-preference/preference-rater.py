import os
import json
from typing import List, Dict, Any, Union
from pydantic import BaseModel, ValidationError
from src.lm.lm import LMService  # Adjust import as needed

# -----------------------------------------------------------------------------
# 1. Pydantic Models
# -----------------------------------------------------------------------------

class ModelRating(BaseModel):
    """
    Represents the rating of a single model for a particular query.
    """
    model_name: str
    rating: float

    class Config:
        # Suppress warnings about the "model_" prefix in field names
        protected_namespaces = ()


class QueryRating(BaseModel):
    """
    Represents a query and the associated model ratings.
    """
    query: str
    model_ratings: List[ModelRating]

    class Config:
        # Suppress warnings about the "model_" prefix in field names
        protected_namespaces = ()


# -----------------------------------------------------------------------------
# 2. Load & Parse Results from Directory
# -----------------------------------------------------------------------------

def load_all_query_ratings(directory: str) -> List[QueryRating]:
    """
    Recursively walks through the given directory to find all .json files
    and attempts to parse them into a list of QueryRating objects.

    Handles two formats:
      1) A standard "ratings" list of the form:
         [
           {
             "query": "Some question",
             "ModelA": 7.2,
             "ModelB": 6.9,
             ...
           },
           ...
         ]

      2) A "detailed_results" file of the form:
         {
           "model_name": "some-model",
           ...
           "detailed_results": [
             {
               "query_index": 0,
               "natural_language_query": "...",
               "ast_score": 0.85,
               ...
             },
             ...
           ]
         }

    Any files that fail to parse or do not match these structures will be skipped.
    Returns a consolidated list of QueryRating objects from all valid files.
    """
    all_ratings: List[QueryRating] = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.lower().endswith(".json"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Failed to load/parse JSON in file: {filepath} — {e}")
                continue

            # CASE 1: We have a list of rating objects
            if isinstance(data, list):
                # Attempt to parse each item as { "query": "...", "<model>": <rating>, ... }
                file_ratings = _parse_standard_rating_list(data, filepath)
                all_ratings.extend(file_ratings)

            # CASE 2: Possibly we have a dict with "detailed_results"
            elif isinstance(data, dict) and "detailed_results" in data:
                file_ratings = _parse_detailed_results_file(data, filepath)
                all_ratings.extend(file_ratings)

            else:
                # Not recognized, skip
                print(f"Skipping file (unrecognized structure): {filepath}")

    return all_ratings


def _parse_standard_rating_list(data: List[Any], filepath: str) -> List[QueryRating]:
    """
    Helper to parse a standard ratings list of the form:
      [
        {
          "query": "Some question",
          "ModelA": 7.2,
          ...
        },
        ...
      ]
    """
    parsed = []
    for item in data:
        if not isinstance(item, dict):
            print(f"Skipping item in {filepath} (not a dict).")
            continue
        if "query" not in item:
            print(f"Skipping item in {filepath} (no 'query' field).")
            continue

        # Convert rating fields (except 'query') into ModelRating
        model_ratings = []
        for model_name, rating_value in item.items():
            if model_name == "query":
                continue
            if not isinstance(rating_value, (int, float)):
                print(f"Skipping non-numeric rating '{rating_value}' for model '{model_name}' in file: {filepath}")
                continue
            model_ratings.append(ModelRating(model_name=model_name, rating=rating_value))

        try:
            qr = QueryRating(query=item["query"], model_ratings=model_ratings)
            parsed.append(qr)
        except ValidationError as ve:
            print(f"Skipping invalid QueryRating in file: {filepath} — {ve}")
            continue
    return parsed


def _parse_detailed_results_file(data: Dict[str, Any], filepath: str) -> List[QueryRating]:
    """
    Helper to parse a "detailed_results" file of the form:
      {
        "model_name": "some-model",
        ...
        "detailed_results": [
          {
            "query_index": 0,
            "natural_language_query": "...",
            "ast_score": 0.85,
            ...
          },
          ...
        ]
      }

    We'll interpret "model_name" from the top-level key,
    "ast_score" as the rating, and "natural_language_query" as the query.
    Customize as needed.
    """
    parsed = []
    top_level_model_name = data.get("model_name", "unknown-model")
    detailed_results = data["detailed_results"]  # type: ignore

    if not isinstance(detailed_results, list):
        print(f"Skipping file (detailed_results is not a list): {filepath}")
        return parsed

    for dr_item in detailed_results:
        if not isinstance(dr_item, dict):
            print(f"Skipping item in {filepath} (not a dict).")
            continue

        # We'll pick "natural_language_query" as the "query"
        # and "ast_score" as the rating.
        # You can adapt these field names as needed.
        query_text = dr_item.get("natural_language_query")
        ast_score = dr_item.get("ast_score")

        if not query_text:
            print(f"Skipping item in {filepath} (no 'natural_language_query').")
            continue
        if not isinstance(ast_score, (int, float)):
            print(f"Skipping item (no numeric 'ast_score') in file: {filepath}")
            continue

        try:
            model_ratings = [ModelRating(model_name=top_level_model_name, rating=ast_score)]
            qr = QueryRating(query=query_text, model_ratings=model_ratings)
            parsed.append(qr)
        except ValidationError as ve:
            print(f"Skipping invalid QueryRating in file: {filepath} — {ve}")
            continue
    return parsed


# -----------------------------------------------------------------------------
# 3. Generate Prompts for Preference
# -----------------------------------------------------------------------------

def get_preference_prompt(query_rating: QueryRating) -> str:
    """
    Given a QueryRating, returns a structured prompt that:
      - Presents the query and the numeric ratings of each model.
      - Asks which model is preferred and why.
      - Requests a JSON-formatted response with "preferred_model" and "reason".
    """
    # Format the model ratings for insertion into the prompt
    model_ratings_text = "\n".join(
        f"- **{mr.model_name}**: {mr.rating}" 
        for mr in query_rating.model_ratings
    )

    prompt = f"""
You are an assistant helping to evaluate language model outputs.

Given the following query and ratings:

- **Query**: {query_rating.query}
{model_ratings_text}

Please indicate which model you prefer and provide a brief explanation.

Respond in the following JSON format:

{{
    "preferred_model": "Name of the preferred model",
    "reason": "Your explanation here."
}}
"""
    return prompt.strip()


# -----------------------------------------------------------------------------
# 4. Call LLM & Log Results
# -----------------------------------------------------------------------------

def rate_preferences(ratings: List[QueryRating], lm_service: LMService) -> List[Dict[str, Any]]:
    """
    For each QueryRating, call the language model with a structured prompt.
    Attempts to parse the response as JSON:
      {
        "preferred_model": "...",
        "reason": "..."
      }

    Returns a list of dicts with the final preferences for each query.
    """
    results = []
    for rating in ratings:
        prompt = get_preference_prompt(rating)
        response = lm_service.generate_response(prompt)
        
        # Try to parse JSON from the LLM's response
        try:
            preference = json.loads(response)
            results.append({
                "query": rating.query,
                "preferred_model": preference.get("preferred_model"),
                "reason": preference.get("reason")
            })
        except json.JSONDecodeError:
            # If the response isn't valid JSON, log the raw response
            print(f"Failed to parse response for query: {rating.query}")
            results.append({
                "query": rating.query,
                "preferred_model": None,
                "reason": response  # store raw response for debugging
            })
    return results


# -----------------------------------------------------------------------------
# 5. Save Results
# -----------------------------------------------------------------------------

def save_results(results: List[Dict[str, Any]], output_file: str) -> None:
    """
    Saves the final results to a JSON file.
    """
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    OPENAI_API_KEY = ""

    # Update these paths as needed
    input_dir = "../../experimental-results"
    output_file = "preference_results.json"

    # 1. Load the ratings from all JSON files in 'experimental-results'
    print(f"Scanning directory for rating JSON files: {input_dir}")
    all_ratings = load_all_query_ratings(input_dir)
    if not all_ratings:
        print("No valid ratings found. Exiting.")
        exit(0)

    # 2. Load the language model service (adjust for your actual initialization)
    lm_service = LMService(
        model_provider="openai",
        api_key=OPENAI_API_KEY
    )

    # 3. Rate preferences
    print(f"Generating preferences with the LLM for {len(all_ratings)} queries...")
    preferences = rate_preferences(all_ratings, lm_service)

    # 4. Save results
    print(f"Saving results to: {output_file}")
    save_results(preferences, output_file)
    print("Done!")
