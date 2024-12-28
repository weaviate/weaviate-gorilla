import os
import json
from typing import List, Dict, Any, Union
from pydantic import BaseModel, ValidationError
from src.lm.lm import LMService  # Adjust import as needed
from colorama import init, Fore  # For colored output

init()  # Initialize colorama

# -----------------------------------------------------------------------------
# 1. Pydantic Models
# -----------------------------------------------------------------------------

class ModelResponse(BaseModel):
    """
    Represents a single model's response to a query.
    This can be a string, or some other structure (dict, list, etc.).
    """
    model_name: str
    response: Union[str, Dict[str, Any], List[Any], None]

    class Config:
        # Suppress warnings about the "model_" prefix in field names
        protected_namespaces = ()


class QueryResponses(BaseModel):
    """
    Represents a query and the associated model responses.
    """
    query: str
    model_responses: List[ModelResponse]

    class Config:
        # Suppress warnings about the "model_" prefix in field names
        protected_namespaces = ()


class PreferenceResponse(BaseModel):
    """
    Structured output format for the LLM's preference rating.
    """
    preferred_model: str
    reason: str

    class Config:
        protected_namespaces = ()


# -----------------------------------------------------------------------------
# 2. Load & Parse Results from Directory
# -----------------------------------------------------------------------------

def load_all_query_responses(directory: str) -> List[QueryResponses]:
    """
    Recursively walks through the given directory to find all .json files
    and attempts to parse them into a list of QueryResponses objects.

    Handles two formats:
      1) A standard "responses" list of the form:
         [
           {
             "query": "Some question",
             "ModelA": "...response from model A...",
             "ModelB": "...response from model B...",
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
               "model_response": "...",
               ...
             },
             ...
           ]
         }

    Any files that fail to parse or do not match these structures will be skipped.
    Returns a consolidated list of QueryResponses objects from all valid files.
    """
    all_responses: List[QueryResponses] = []

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

            # CASE 1: We have a list of response objects
            if isinstance(data, list):
                file_responses = _parse_standard_response_list(data, filepath)
                all_responses.extend(file_responses)

            # CASE 2: Possibly we have a dict with "detailed_results"
            elif isinstance(data, dict) and "detailed_results" in data:
                file_responses = _parse_detailed_results_file(data, filepath)
                all_responses.extend(file_responses)

            else:
                # Not recognized, skip
                print(f"Skipping file (unrecognized structure): {filepath}")

    return all_responses


def _parse_standard_response_list(data: List[Any], filepath: str) -> List[QueryResponses]:
    """
    Helper to parse a standard responses list of the form:
      [
        {
          "query": "Some question",
          "ModelA": "...",
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

        # Convert response fields (except 'query') into ModelResponse
        model_responses = []
        for model_name, response_value in item.items():
            if model_name == "query":
                continue
            # In this revised version, we allow any type but store it directly
            model_responses.append(ModelResponse(model_name=model_name, response=response_value))

        try:
            qr = QueryResponses(query=item["query"], model_responses=model_responses)
            parsed.append(qr)
        except ValidationError as ve:
            print(f"Skipping invalid QueryResponses in file: {filepath} — {ve}")
            continue
    return parsed


def _parse_detailed_results_file(data: Dict[str, Any], filepath: str) -> List[QueryResponses]:
    """
    Helper to parse a "detailed_results" file of the form:
      {
        "model_name": "some-model",
        ...
        "detailed_results": [
          {
            "query_index": 0,
            "natural_language_query": "...",
            "model_response": "...",
            ...
          },
          ...
        ]
      }
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

        query_text = dr_item.get("natural_language_query")
        # "model_response" or "response" can be any type now
        model_response = dr_item.get("model_response") or dr_item.get("response")

        if not query_text:
            print(f"Skipping item in {filepath} (no 'natural_language_query').")
            continue

        # We'll store whatever type is there, whether string, dict, list, etc.
        try:
            model_responses = [ModelResponse(model_name=top_level_model_name, response=model_response)]
            qr = QueryResponses(query=query_text, model_responses=model_responses)
            parsed.append(qr)
        except ValidationError as ve:
            print(f"Skipping invalid QueryResponses in file: {filepath} — {ve}")
            continue
    return parsed


# -----------------------------------------------------------------------------
# 3. Generate Prompts for Preference
# -----------------------------------------------------------------------------

def get_preference_prompt(query_responses: QueryResponses) -> str:
    """
    Given a QueryResponses, returns a structured prompt that:
      - Presents the query and each model's response
      - Asks which model response is preferred and why
      - Requests a JSON-formatted response with "preferred_model" and "reason"
    """
    # Format the model responses for insertion into the prompt.
    # If the response is not a string, we'll convert it to JSON for display.
    model_responses_text = ""
    for mr in query_responses.model_responses:
        if isinstance(mr.response, str):
            display_response = mr.response
        else:
            display_response = json.dumps(mr.response, indent=2)
        model_responses_text += f"- **{mr.model_name}**:\n{display_response}\n\n"

    prompt = f"""
You are an assistant helping to evaluate language model outputs.

Given the following query and model responses:

- **Query**: {query_responses.query}

{model_responses_text}

Please indicate which model's response you prefer and provide a brief explanation.
Consider factors like accuracy, clarity, completeness, and relevance to the query.

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

def rate_preferences(responses: List[QueryResponses], lm_service: LMService) -> List[Dict[str, Any]]:
    """
    For each QueryResponses, call the language model with a structured prompt.
    We do a raw response generation, parse JSON, then validate with PreferenceResponse.
    """
    results = []
    for response_set in responses:
        prompt = get_preference_prompt(response_set)
        
        # Generate raw text from the LLM
        raw_response = lm_service.generate_response(prompt)

        # Parse as JSON, then validate with PreferenceResponse
        try:
            parsed_json = json.loads(raw_response)
            preference_obj = PreferenceResponse(**parsed_json)
            results.append({
                "query": response_set.query,
                "model_responses": {
                    mr.model_name: mr.response
                    for mr in response_set.model_responses
                },
                "preferred_model": preference_obj.preferred_model,
                "reason": preference_obj.reason,
            })
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Warning: Could not parse or validate LLM response for query: {response_set.query} — {e}")
            results.append({
                "query": response_set.query,
                "model_responses": {
                    mr.model_name: mr.response
                    for mr in response_set.model_responses
                },
                "preferred_model": None,
                "reason": raw_response  # fallback: store raw text
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

    # 1. Load the responses from all JSON files in 'experimental-results'
    print(f"Scanning directory for response JSON files: {input_dir}")
    all_responses = load_all_query_responses(input_dir)
    if not all_responses:
        print("No valid responses found. Exiting.")
        exit(0)

    # Print a sample of the first response to verify loading
    if all_responses:
        print(f"\n{Fore.GREEN}Successfully loaded responses! Here's a sample of the first record:")
        sample = all_responses[0]
        print(f"Query: {sample.query}")
        print("Model Responses:")
        for mr in sample.model_responses:
            print(f"- {mr.model_name}: {mr.response[:100]}..." if isinstance(mr.response, str) else f"- {mr.model_name}: {type(mr.response)}")
        print(f"{Fore.RESET}\n")

    # 2. Load the language model service
    lm_service = LMService(
        model_provider="openai",
        model_name="gpt-4",
        api_key=OPENAI_API_KEY
    )

    # 3. Rate preferences
    print(f"Generating preferences with the LLM for {len(all_responses)} queries...")
    preferences = rate_preferences(all_responses, lm_service)

    # 4. Save results
    print(f"Saving results to: {output_file}")
    save_results(preferences, output_file)
    print("Done!")
