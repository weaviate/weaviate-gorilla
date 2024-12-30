import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel, ValidationError, create_model, ConfigDict
from colorama import init, Fore  # For colored output
from collections import defaultdict

# If you have your own LMService class, adjust import below as needed
from src.lm.lm import LMService  

init()  # Initialize colorama

# -----------------------------------------------------------------------------
# 1. Existing Pydantic Models for Predictions
# -----------------------------------------------------------------------------

class LLMPrediction(BaseModel):
    """
    Represents a single model's prediction
    """
    llm_name: str  
    predicted_query: str

    class Config:
        protected_namespaces = ()

class QueryPredictions(BaseModel):
    """
    Represents a natural language query and predictions from different models
    """
    corresponding_natural_language_query: str
    predictions: List[LLMPrediction]

    class Config:
        protected_namespaces = ()

# -----------------------------------------------------------------------------
# 2A. Gather All LLMs + Load & Parse Results 
# -----------------------------------------------------------------------------

def gather_all_llm_names(directory: str) -> set:
    """
    Scans the directory for all JSON files, returns a set of all LLM names
    discovered (based on filenames).
    """
    all_llm_names = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".json"):
                model_name = os.path.splitext(file)[0]
                all_llm_names.add(model_name)
    return all_llm_names

def load_all_query_predictions(directory: str) -> List[QueryPredictions]:
    """
    Walks through directory to find .json files and parses them into QueryPredictions objects.
    Each file represents predictions from a different model.
    """
    query_predictions: Dict[str, List[LLMPrediction]] = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.lower().endswith('.json'):
                continue
                
            filepath = os.path.join(root, file)
            model_name = os.path.splitext(file)[0]  # Remove .json extension
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Failed to load/parse JSON in file: {filepath} — {e}")
                continue

            if not isinstance(data, dict) or "detailed_results" not in data:
                print(f"Skipping file (unrecognized structure): {filepath}")
                continue

            for result in data["detailed_results"]:
                query = result.get("natural_language_query")
                predicted = result.get("predicted_query")
                
                if not query or not predicted:
                    continue
                    
                # Convert prediction to string format
                predicted_str = json.dumps(predicted, sort_keys=True)
                
                prediction = LLMPrediction(
                    llm_name=model_name,
                    predicted_query=predicted_str
                )
                
                if query not in query_predictions:
                    query_predictions[query] = []
                query_predictions[query].append(prediction)

    # Convert to list of QueryPredictions
    all_predictions = []
    for query, preds in query_predictions.items():
        # Only include queries with multiple predictions
        if len(preds) > 1:
            all_predictions.append(QueryPredictions(
                corresponding_natural_language_query=query,
                predictions=preds
            ))

    return all_predictions

# -----------------------------------------------------------------------------
# 3. Dynamic Prompt Generation for Strict JSON
# -----------------------------------------------------------------------------

def get_dynamic_preference_prompt(query_predictions: QueryPredictions) -> str:
    """
    Creates a prompt instructing the LLM to produce a JSON object with:
      - a 'rationale' field (a string explanation)
      - one integer field for each LLM name discovered
        (1 = best rank, 2 = second best, etc.)
    """
    predictions_text = ""
    llm_names = [pred.llm_name for pred in query_predictions.predictions]

    for pred in query_predictions.predictions:
        predictions_text += f"- **{pred.llm_name}**:\n{pred.predicted_query}\n\n"

    llm_fields_str = "\n".join([f'  "{name}": <integer rank>' for name in llm_names])

    prompt = f"""
You are an expert at evaluating database query predictions.

Given this natural language query:

{query_predictions.corresponding_natural_language_query}

We have the following model predictions:

{predictions_text}

You must produce valid JSON with:
- A top-level field named "rationale" (a string explanation of your ranking decisions)
- One integer field for each LLM name, with no extra fields.

For example:
{{
  "rationale": "some explanation",
{llm_fields_str}
}}

Where:
- "rationale" is a string
- Each LLM name is a required integer rank (1 = best, 2 = next best, etc.)
- No other keys are allowed
- All discovered LLMs must appear exactly once
- Provide unique ranks (no ties).

IMPORTANT: Respond ONLY with the JSON object, no additional text or formatting.
"""
    return prompt.strip()

# -----------------------------------------------------------------------------
# 4. Dynamically Build a Pydantic Model for Strict Validation
# -----------------------------------------------------------------------------

def build_dynamic_preference_model(llm_names: List[str]) -> BaseModel:
    """
    Creates a dynamic Pydantic model with the following schema:
      rationale: str (required)
      <llm_name_1>: int (required)
      <llm_name_2>: int (required)
      ...
    Extra fields are forbidden.
    """
    field_definitions = {
        "rationale": (str, ...),  # required string
    }
    for name in llm_names:
        field_definitions[name] = (int, ...)  # required integer rank

    model_config = ConfigDict(extra="forbid")

    DynamicPreferenceModel = create_model(
        "DynamicPreferenceModel",
        __config__=model_config,
        **field_definitions
    )
    return DynamicPreferenceModel

# -----------------------------------------------------------------------------
# 5. Call LLM & Log Results, Tying Missing LLMs for Last
# -----------------------------------------------------------------------------

def rate_preferences(
    predictions: List[QueryPredictions], 
    lm_service: LMService,
    all_llm_names: set
) -> List[Dict[str, Any]]:
    """
    For each QueryPredictions, call the language model with the new structured prompt,
    parse the response with a dynamically created model, and store the final results.

    If some LLMs do not appear in this query, we log that they're missing and 
    tie them for last place in the final ranking.
    """
    results = []
    current_standings = defaultdict(lambda: defaultdict(int))
    
    for idx, pred_set in enumerate(predictions):
        print(f"\n{Fore.CYAN}Processing query: {pred_set.corresponding_natural_language_query}{Fore.RESET}")

        # LLMs that actually have predictions for this query
        present_llms = [p.llm_name for p in pred_set.predictions]
        # LLMs that are missing from this query
        missing_llms = all_llm_names - set(present_llms)

        # Log if some are missing
        if missing_llms:
            print(f"{Fore.YELLOW}Warning: The following LLMs did NOT predict this query: {missing_llms}{Fore.RESET}")

        # 1) Build the dynamic model for only the present LLMs
        DynamicPreferenceModel = build_dynamic_preference_model(present_llms)
        
        # 2) Get the dynamic prompt
        prompt = get_dynamic_preference_prompt(pred_set)

        # 3) Generate response from LLM with output model
        preference_obj = lm_service.generate(prompt=prompt, output_model=DynamicPreferenceModel)

        # We'll store final model->rank mapping here
        final_rank_dict: Dict[str, int] = {}

        try:
            # Extract fields from the validated model (the ones that are present)
            pref_dict = preference_obj.model_dump()
            rationale = pref_dict.pop("rationale")

            # Sort by rank
            sorted_model_ranks = sorted(pref_dict.items(), key=lambda x: x[1])
            # Convert to a best-to-worst list
            model_rankings_ordered = [m for (m, r) in sorted_model_ranks]

            # Build the rank dict for the present LLMs
            for model_name, rank in sorted_model_ranks:
                final_rank_dict[model_name] = rank

            # 4) For each missing LLM, tie them for "last place"
            if missing_llms:
                # The largest rank among present LLMs
                # If no present LLMs, we can default to 1
                if sorted_model_ranks:
                    last_rank = max(r for (_, r) in sorted_model_ranks)
                else:
                    last_rank = 1

                # Tie all missing LLMs for last (last_rank + 1, if you prefer)
                # We'll do last_rank+1 so it's strictly worse than the existing last
                tie_rank = last_rank + 1

                for missing_model in missing_llms:
                    final_rank_dict[missing_model] = tie_rank
                    model_rankings_ordered.append(missing_model)

                print(f"{Fore.YELLOW}Tying missing LLMs {missing_llms} for rank {tie_rank}.{Fore.RESET}")

            # Now we have a combined ranking for present + missing
            # final_rank_dict is a dict of all LLM -> rank
            # model_rankings_ordered is an array of LLMs in best-to-worst order
            # But it might not be strictly sorted if we appended missing at the end.
            # Let's do one final sorted pass to get a pure best-to-worst order:
            final_sorted = sorted(final_rank_dict.items(), key=lambda x: x[1])
            final_model_rankings = [m for (m, r) in final_sorted]

            print(f"{Fore.GREEN}Rationale: {rationale}{Fore.RESET}")
            print(f"{Fore.GREEN}All LLM Ranks: {final_sorted}{Fore.RESET}")

            # Update current standings
            for rank, model in enumerate(final_model_rankings, 1):
                current_standings[model][rank] += 1

            # Print standings every 10 queries
            if (idx + 1) % 10 == 0:
                print(f"\n{'='*50}")
                print(f"{Fore.CYAN}Current Standings after {idx + 1} queries:{Fore.RESET}")
                print(f"{'='*50}")
                
                # Calculate weighted scores for each model
                # Score formula: 
                # - 1st place = 100 points
                # - 2nd place = 70 points
                # - 3rd place = 50 points
                # - 4th place = 35 points
                # - 5th+ place = max(25 - (rank-5)*5, 0) points
                # This creates a steep dropoff for top positions while still rewarding
                # consistent mid-tier performance over last-place finishes
                model_scores = {}
                for model in current_standings.keys():
                    score = 0
                    for rank, count in current_standings[model].items():
                        if rank == 1:
                            score += count * 100
                        elif rank == 2:
                            score += count * 70
                        elif rank == 3:
                            score += count * 50
                        elif rank == 4:
                            score += count * 35
                        else:
                            score += count * max(25 - (rank-5)*5, 0)
                    model_scores[model] = score
                
                # Sort models by score and first place finishes
                models_sorted = sorted(
                    current_standings.keys(),
                    key=lambda m: (-model_scores[m], -current_standings[m][1], m)
                )
                
                for model in models_sorted:
                    first_places = current_standings[model][1]
                    first_place_pct = (first_places / (idx + 1)) * 100
                    score = model_scores[model]
                    print(f"{model}: Score {score:.0f} | {first_places} first places ({first_place_pct:.1f}%)")
                print(f"{'='*50}\n")

            # 5) Append final result
            results.append({
                "query": pred_set.corresponding_natural_language_query,
                "model_predictions": {
                    pred.llm_name: pred.predicted_query
                    for pred in pred_set.predictions
                },
                "model_rankings": final_model_rankings,
                "model_ranks_dict": final_rank_dict,
                "reason": rationale,
            })

        except (ValidationError, TypeError) as e:
            # If something went wrong, log it
            print(f"{Fore.RED}Could not parse/validate response for query: {pred_set.corresponding_natural_language_query} — {e}{Fore.RESET}")
            results.append({
                "query": pred_set.corresponding_natural_language_query,
                "model_predictions": {
                    pred.llm_name: pred.predicted_query
                    for pred in pred_set.predictions
                },
                "model_rankings": None,
                "reason": str(e)
            })
    
    return results

# -----------------------------------------------------------------------------
# 6. Save Results
# -----------------------------------------------------------------------------

def save_results(results: List[Dict[str, Any]], output_file: str) -> None:
    """
    Saves the final results to a JSON file.
    """
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

# -----------------------------------------------------------------------------
# 7. Analyze Rankings
# -----------------------------------------------------------------------------

def analyze_rankings(preferences: List[Dict[str, Any]]) -> None:
    """
    Analyzes the ranking results to show overall model performance.
    Now that we append missing LLMs with last-rank,
    they will appear in the final analysis as well.
    """
    rank_counts = defaultdict(lambda: defaultdict(int))  # model -> rank position -> count
    total_valid_rankings = 0
    model_names = set()

    for pref in preferences:
        rankings = pref.get("model_rankings")
        if rankings:
            total_valid_rankings += 1
            for rank, model in enumerate(rankings, 1):
                rank_counts[model][rank] += 1
                model_names.add(model)

    if not total_valid_rankings:
        print(f"\n{Fore.RED}No valid rankings found to analyze{Fore.RESET}")
        return

    print(f"\n{Fore.CYAN}Ranking Analysis:")
    print(f"Total queries with valid rankings: {total_valid_rankings}{Fore.RESET}\n")

    # Sort models by number of first-place finishes
    models_by_first_place = sorted(
        model_names,
        key=lambda m: (-rank_counts[m][1], m)
    )

    for model in models_by_first_place:
        first_place = rank_counts[model][1]
        first_place_pct = (first_place / total_valid_rankings) * 100
        
        print(f"{Fore.GREEN}{model}:")
        print(f"  First place: {first_place} times ({first_place_pct:.1f}%)")
        
        # Show distribution across ranks
        print("  Rank distribution:")
        for rank in range(1, len(model_names) + 1):
            count = rank_counts[model][rank]
            pct = (count / total_valid_rankings) * 100
            print(f"    Rank {rank}: {count} times ({pct:.1f}%)")
        print(f"{Fore.RESET}")

# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    OPENAI_API_KEY = ""
    
    # Update these paths as needed
    input_dir = "../../experimental-results"
    output_file = "preference_results.json"

    # 1. Gather all possible LLM names from the directory
    all_llm_names = gather_all_llm_names(input_dir)
    print(f"All discovered LLM names in directory: {all_llm_names}")

    # 2. Load the predictions from all JSON files
    print(f"Scanning directory for prediction JSON files: {input_dir}")
    all_predictions = load_all_query_predictions(input_dir)
    if not all_predictions:
        print("No valid predictions found. Exiting.")
        exit(0)

    # Print a sample of the first prediction to verify loading
    if all_predictions:
        print(f"\n{Fore.GREEN}Successfully loaded predictions! Here's a sample of the first record:")
        sample = all_predictions[0]
        print(f"Query: {sample.corresponding_natural_language_query}")
        print("Model Predictions:")
        for pred in sample.predictions:
            print(f"- {pred.llm_name}:\n{pred.predicted_query}")
        print(f"{Fore.RESET}\n")

    # 3. Analyze prediction differences (purely informational)
    print("\nAnalyzing prediction differences across models...")
    total_queries = len(all_predictions)
    queries_with_differences = 0
    queries_printed = 0
    
    for query_pred in all_predictions:
        unique_predictions = set(pred.predicted_query for pred in query_pred.predictions)
        if len(unique_predictions) > 1:
            queries_with_differences += 1
            if queries_printed < 10:
                print(f"\n{Fore.RED}Query with differing predictions:")
                print(f"Query: {query_pred.corresponding_natural_language_query}")
                print(f"Number of unique predictions: {len(unique_predictions)}{Fore.RESET}")
                queries_printed += 1
    
    print(f"\n{Fore.CYAN}Summary:")
    print(f"Total queries analyzed: {total_queries}")
    print(f"Queries with differing predictions: {queries_with_differences} ({(queries_with_differences/total_queries)*100:.1f}%)")
    print(f"Queries with identical predictions: {total_queries - queries_with_differences} ({((total_queries-queries_with_differences)/total_queries)*100:.1f}%){Fore.RESET}\n")

    # 4. Initialize the language model service
    lm_service = LMService(
        model_provider="openai",
        model_name="gpt-4o",
        api_key=OPENAI_API_KEY
    )

    # 5. Rate preferences (tie missing LLMs for last)
    print(f"Generating preferences with the LLM for {len(all_predictions)} queries...")
    preferences = rate_preferences(all_predictions, lm_service, all_llm_names)

    # 6. Save results
    print(f"Saving results to: {output_file}")
    save_results(preferences, output_file)

    # 7. Analyze rankings
    analyze_rankings(preferences)
    print("Done!")