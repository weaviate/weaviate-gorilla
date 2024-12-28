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
    preferred_model: str
    reason: str

    class Config:
        protected_namespaces = ()

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
You are an assistant helping to evaluate language model outputs.

Given the following query and model predictions:

- **Query**: {query_predictions.corresponding_natural_language_query}

{predictions_text}

Please indicate which model's prediction you prefer and provide a brief explanation.
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

def rate_preferences(predictions: List[QueryPredictions], lm_service: LMService) -> List[Dict[str, Any]]:
    """
    For each QueryPredictions, call the language model with a structured prompt.
    """
    results = []
    for pred_set in predictions:
        prompt = get_preference_prompt(pred_set)
        
        # Generate raw text from the LLM
        raw_response = lm_service.generate_response(prompt)

        try:
            parsed_json = json.loads(raw_response)
            preference_obj = PreferenceResponse(**parsed_json)
            results.append({
                "query": pred_set.corresponding_natural_language_query,
                "model_predictions": {
                    pred.model_name: pred.predicted_query
                    for pred in pred_set.predictions
                },
                "preferred_model": preference_obj.preferred_model,
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
