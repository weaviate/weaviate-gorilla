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

class LLMPrediction(BaseModel):
    """
    Represents a single model's prediction
    """
    model_name: str  
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

class PreferenceResponse(BaseModel):
    """
    Structured output format for the LLM's preference rating.
    """
    model_rankings: List[str]  # List of model names in order of preference
    reason: str

# -----------------------------------------------------------------------------
# 2. Load & Parse Results from Directory 
# -----------------------------------------------------------------------------

def load_all_query_predictions(directory: str) -> List[QueryPredictions]:
    """
    Walks through directory to find .json files and parses them into QueryPredictions objects.
    Each file represents predictions from a different model.
    """
    # First collect all predictions by query
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
                    model_name=model_name,
                    predicted_query=predicted_str
                )
                
                if query not in query_predictions:
                    query_predictions[query] = []
                query_predictions[query].append(prediction)

    # Convert to list of QueryPredictions
    all_predictions = []
    for query, predictions in query_predictions.items():
        if len(predictions) > 1:  # Only include queries with multiple predictions to compare
            qp = QueryPredictions(
                corresponding_natural_language_query=query,
                predictions=predictions
            )
            all_predictions.append(qp)

    return all_predictions

# -----------------------------------------------------------------------------
# 3. Generate Prompts for Preference
# -----------------------------------------------------------------------------

def get_preference_prompt(query_predictions: QueryPredictions) -> str:
    """
    Creates a prompt showing the query and each model's predicted query,
    asking which prediction is preferred and why.
    """
    predictions_text = ""
    for pred in query_predictions.predictions:
        predictions_text += f"- **{pred.model_name}**:\n{pred.predicted_query}\n\n"

    prompt = f"""
You are an expert at evaluating database query predictions.

Given this natural language query and the different model predictions:

- **Original Query**: {query_predictions.corresponding_natural_language_query}

Model Predictions:
{predictions_text}

Please rank the models from best to worst based on how well their predicted queries match the intent of the original question.
Consider:
- Accuracy in capturing the query intent
- Correctness of filters and aggregations
- Proper handling of grouping if required

Respond in the following JSON format:

{{
    "model_rankings": ["best_model", "second_best", ...],
    "reason": "Detailed explanation of your ranking decisions"
}}
"""
    return prompt.strip()

# -----------------------------------------------------------------------------
# 4. Call LLM & Log Results
# -----------------------------------------------------------------------------

def rate_preferences(predictions: List[QueryPredictions], lm_service: LMService) -> List[Dict[str, Any]]:
    """
    For each QueryPredictions, call the language model with a structured prompt.
    """
    results = []
    for pred_set in predictions:
        prompt = get_preference_prompt(pred_set)
        
        # Generate raw text from the LLM
        raw_response = lm_service.generate(prompt=prompt, output_model=PreferenceResponse)

        try:
            # If response is already a dict, no need to parse
            if isinstance(raw_response, dict):
                preference_obj = PreferenceResponse(**raw_response)
            else:
                parsed_json = json.loads(raw_response)
                preference_obj = PreferenceResponse(**parsed_json)
                
            results.append({
                "query": pred_set.corresponding_natural_language_query,
                "model_predictions": {
                    pred.model_name: pred.predicted_query
                    for pred in pred_set.predictions
                },
                "model_rankings": preference_obj.model_rankings,
                "reason": preference_obj.reason,
            })
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Warning: Could not parse or validate LLM response for query: {pred_set.corresponding_natural_language_query} — {e}")
            results.append({
                "query": pred_set.corresponding_natural_language_query,
                "model_predictions": {
                    pred.model_name: pred.predicted_query
                    for pred in pred_set.predictions
                },
                "model_rankings": None,
                "reason": str(raw_response)  # fallback: store raw text
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

    # 1. Load the predictions from all JSON files
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
            print(f"- {pred.model_name}:\n{pred.predicted_query}")
        print(f"{Fore.RESET}\n")

    # Analyze prediction differences
    print("\nAnalyzing prediction differences across models...")
    total_queries = len(all_predictions)
    queries_with_differences = 0
    queries_printed = 0
    
    for query_pred in all_predictions:
        # Get unique predictions for this query
        unique_predictions = set(pred.predicted_query for pred in query_pred.predictions)
        if len(unique_predictions) > 1:  # If there are different predictions
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

    # 2. Load the language model service
    lm_service = LMService(
        model_provider="openai",
        model_name="gpt-4o",
        api_key=OPENAI_API_KEY
    )

    # 3. Rate preferences
    print(f"Generating preferences with the LLM for {len(all_predictions)} queries...")
    preferences = rate_preferences(all_predictions, lm_service)

    # 4. Save results
    print(f"Saving results to: {output_file}")
    save_results(preferences, output_file)
    print("Done!")
