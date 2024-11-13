# placeholder

# calculate per API binary accuracy from serialized test

import json
from typing import Dict, List, Optional
from pydantic import BaseModel

# Load experiment results
with open("../gpt-4o-mini-experiment-results.json", "r") as f:
    results = json.load(f)

total_queries = 0
correct_filters = 0

# Analyze each query result
for result in results["detailed_results"]:
    total_queries += 1
    
    # Skip if prediction failed
    if result["predicted_query"] is None:
        continue
        
    ground_truth = result["ground_truth_query"]
    prediction = result["predicted_query"]
    
    # Compare filters
    filters_match = True
    
    # Check integer filters
    if ground_truth["integer_property_filter"] != prediction["integer_property_filter"]:
        filters_match = False
        
    # Check text filters    
    if ground_truth["text_property_filter"] != prediction["text_property_filter"]:
        filters_match = False
        
    # Check boolean filters
    if ground_truth["boolean_property_filter"] != prediction["boolean_property_filter"]:
        filters_match = False
        
    if filters_match:
        correct_filters += 1

# Calculate accuracy
filter_accuracy = correct_filters / total_queries

print(f"Total queries analyzed: {total_queries}")
print(f"Queries with correct filters: {correct_filters}")
print(f"Filter accuracy: {filter_accuracy:.2%}")
