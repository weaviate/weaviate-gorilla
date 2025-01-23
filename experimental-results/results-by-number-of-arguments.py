# Calculate per API accuracy from perfect matches

import json
import os
from typing import Dict, List, Optional
from pydantic import BaseModel
from collections import defaultdict

# Process all result files in the results folder
results_dir = "results"
for filename in os.listdir(results_dir):
    if not filename.endswith('.json'):
        continue
        
    print(f"\nAnalyzing {filename}...")
    
    # Load experiment results
    with open(os.path.join(results_dir, filename), "r") as f:
        results = json.load(f)

    total_queries = results["total_queries"]
    successful_predictions = results["successful_predictions"] 
    failed_predictions = results["failed_predictions"]
    average_ast_score = results["average_ast_score"]
    exact_match_pct = results["exact_match_pct"]
    collection_routing_pct = results["collection_routing_accuracy"]

    # Print summary statistics
    print(f"Total queries analyzed: {total_queries}")
    print(f"Exact Match pct: {exact_match_pct}")
    print(f"Collection Routing pct: {collection_routing_pct}")
    print(f"Successful predictions: {successful_predictions}")
    print(f"Failed predictions: {failed_predictions}")
    print(f"Average AST score: {average_ast_score:.2%}")

    # Initialize lists for each category
    category_1_arg = []
    category_2_args = []
    category_3_plus_args = []

    # Count arguments and collect perfect matches for each query
    for result in results["detailed_results"]:
        ground_truth = result["ground_truth_query"]
        # Perfect match is when AST score is 1.0
        perfect_match = 1 if result["ast_score"] == 1.0 else 0
        
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
            category_1_arg.append(perfect_match)
        elif num_args == 2:
            category_2_args.append(perfect_match)
        elif num_args >= 3:
            category_3_plus_args.append(perfect_match)

    # Print analysis by number of arguments
    print("\nAnalysis by number of arguments (perfect matches):")
    if category_1_arg:
        perfect_matches = sum(category_1_arg)
        print(f"Simple queries (1 argument): {perfect_matches}/{len(category_1_arg)} ({perfect_matches/len(category_1_arg):.2%})")
    if category_2_args:
        perfect_matches = sum(category_2_args)
        print(f"Intermediate queries (2 arguments): {perfect_matches}/{len(category_2_args)} ({perfect_matches/len(category_2_args):.2%})")
    if category_3_plus_args:
        perfect_matches = sum(category_3_plus_args)
        print(f"Complex queries (3+ arguments): {perfect_matches}/{len(category_3_plus_args)} ({perfect_matches/len(category_3_plus_args):.2%})")
