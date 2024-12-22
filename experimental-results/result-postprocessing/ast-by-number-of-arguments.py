# Calculate per API accuracy from AST scores

import json
from typing import Dict, List, Optional
from pydantic import BaseModel
from collections import defaultdict

# Load experiment results
with open("../Llama-3.1-8B-Instruct-Turbo.json", "r") as f:
    results = json.load(f)

total_queries = results["total_queries"]
successful_predictions = results["successful_predictions"] 
failed_predictions = results["failed_predictions"]
average_ast_score = results["average_ast_score"]

# Print summary statistics
print(f"Total queries analyzed: {total_queries}")
print(f"Successful predictions: {successful_predictions}")
print(f"Failed predictions: {failed_predictions}")
print(f"Average AST score: {average_ast_score:.2%}")

# Initialize lists for each category
category_1_arg = []
category_2_args = []
category_3_plus_args = []

# Count arguments and collect scores for each query
for result in results["detailed_results"]:
    ground_truth = result["ground_truth_query"]
    ast_score = result["ast_score"]
    
    # Count number of arguments used
    num_args = 0
    if ground_truth["search_query"]:
        num_args += 1
    if ground_truth["integer_property_filter"]:
        num_args += 1
    if ground_truth["text_property_filter"]:
        num_args += 1
    if ground_truth["boolean_property_filter"]:
        num_args += 1
    if ground_truth["integer_property_aggregation"]:
        num_args += 1
    if ground_truth["text_property_aggregation"]:
        num_args += 1
    if ground_truth["boolean_property_aggregation"]:
        num_args += 1
    if ground_truth["groupby_property"]:
        num_args += 1
        
    # Categorize based on number of arguments
    if num_args == 1:
        category_1_arg.append(ast_score)
    elif num_args == 2:
        category_2_args.append(ast_score)
    elif num_args >= 3:
        category_3_plus_args.append(ast_score)

# Print analysis by number of arguments
print("\nAnalysis by number of arguments:")
if category_1_arg:
    print(f"Queries with 1 argument ({len(category_1_arg)}): {sum(category_1_arg)/len(category_1_arg):.2%}")
if category_2_args:
    print(f"Queries with 2 arguments ({len(category_2_args)}): {sum(category_2_args)/len(category_2_args):.2%}")
if category_3_plus_args:
    print(f"Queries with 3+ arguments ({len(category_3_plus_args)}): {sum(category_3_plus_args)/len(category_3_plus_args):.2%}")
