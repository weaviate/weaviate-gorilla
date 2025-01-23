# Calculate per API accuracy from AST scores

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

    # Print summary statistics
    print(f"Total queries analyzed: {total_queries}")
    print(f"Successful predictions: {successful_predictions}")
    print(f"Failed predictions: {failed_predictions}")
    print(f"Average AST score: {average_ast_score:.2%}")
    print(f"Exact match percentage: {exact_match_pct:.2%}")

    # Calculate per schema exact matches
    schema_exact_matches = defaultdict(list)
    for result in results["detailed_results"]:
        schema_idx = result["database_schema_index"]
        # Perfect match is when AST score is 1.0
        exact_match = 1 if result["ast_score"] == 1.0 else 0
        schema_exact_matches[str(schema_idx)].append(exact_match)
    
    # Calculate exact match percentage for each schema
    per_schema_exact_matches = {
        schema_id: sum(matches)/len(matches) 
        for schema_id, matches in schema_exact_matches.items()
    }
    
    # Print per schema exact match percentages
    print("\nPer schema exact matches:")
    for schema_id, pct in per_schema_exact_matches.items():
        matches = schema_exact_matches[schema_id]
        print(f"Schema {schema_id}: {sum(matches)}/{len(matches)} ({pct:.2%})")

    # Analyze query components
    queries_with_search = []
    queries_with_int_filter = []
    queries_with_text_filter = []
    queries_with_bool_filter = []
    queries_with_int_agg = []
    queries_with_text_agg = []
    queries_with_bool_agg = []
    queries_with_groupby = []

    # Collect exact matches for each component
    for result in results["detailed_results"]:
        ground_truth = result["ground_truth_query"]
        # Perfect match is when AST score is 1.0
        perfect_match = 1 if result["ast_score"] == 1.0 else 0
        
        if ground_truth["search_query"]:
            queries_with_search.append(perfect_match)
        if ground_truth["integer_property_filter"]:
            queries_with_int_filter.append(perfect_match)
        if ground_truth["text_property_filter"]:
            queries_with_text_filter.append(perfect_match)
        if ground_truth["boolean_property_filter"]:
            queries_with_bool_filter.append(perfect_match)
        if ground_truth["integer_property_aggregation"]:
            queries_with_int_agg.append(perfect_match)
        if ground_truth["text_property_aggregation"]:
            queries_with_text_agg.append(perfect_match)
        if ground_truth["boolean_property_aggregation"]:
            queries_with_bool_agg.append(perfect_match)
        if ground_truth["groupby_property"]:
            queries_with_groupby.append(perfect_match)

    # Print component analysis
    print("\nPer component analysis (exact matches):")
    if queries_with_search:
        perfect_matches = sum(queries_with_search)
        print(f"Queries with search: {perfect_matches}/{len(queries_with_search)} ({perfect_matches/len(queries_with_search):.2%})")
    if queries_with_int_filter:
        perfect_matches = sum(queries_with_int_filter)
        print(f"Queries with integer filters: {perfect_matches}/{len(queries_with_int_filter)} ({perfect_matches/len(queries_with_int_filter):.2%})")
    if queries_with_text_filter:
        perfect_matches = sum(queries_with_text_filter)
        print(f"Queries with text filters: {perfect_matches}/{len(queries_with_text_filter)} ({perfect_matches/len(queries_with_text_filter):.2%})")
    if queries_with_bool_filter:
        perfect_matches = sum(queries_with_bool_filter)
        print(f"Queries with boolean filters: {perfect_matches}/{len(queries_with_bool_filter)} ({perfect_matches/len(queries_with_bool_filter):.2%})")
    if queries_with_int_agg:
        perfect_matches = sum(queries_with_int_agg)
        print(f"Queries with integer aggregations: {perfect_matches}/{len(queries_with_int_agg)} ({perfect_matches/len(queries_with_int_agg):.2%})")
    if queries_with_text_agg:
        perfect_matches = sum(queries_with_text_agg)
        print(f"Queries with text aggregations: {perfect_matches}/{len(queries_with_text_agg)} ({perfect_matches/len(queries_with_text_agg):.2%})")
    if queries_with_bool_agg:
        perfect_matches = sum(queries_with_bool_agg)
        print(f"Queries with boolean aggregations: {perfect_matches}/{len(queries_with_bool_agg)} ({perfect_matches/len(queries_with_bool_agg):.2%})")
    if queries_with_groupby:
        perfect_matches = sum(queries_with_groupby)
        print(f"Queries with groupby: {perfect_matches}/{len(queries_with_groupby)} ({perfect_matches/len(queries_with_groupby):.2%})")
