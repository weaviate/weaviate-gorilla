# Calculate per API accuracy from AST scores

import json
from typing import Dict, List, Optional
from pydantic import BaseModel
from collections import defaultdict

# Load experiment results
with open("../gpt-4o-mini-experiment-results.json", "r") as f:
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

# Print per schema scores
print("\nPer schema scores:")
for schema_id, score in results["per_schema_scores"].items():
    print(f"Schema {schema_id}: {score:.2%}")

# Analyze query components
queries_with_search = []
queries_with_int_filter = []
queries_with_text_filter = []
queries_with_bool_filter = []
queries_with_int_agg = []
queries_with_text_agg = []
queries_with_bool_agg = []
queries_with_groupby = []

# Collect scores for each component
for result in results["detailed_results"]:
    ground_truth = result["ground_truth_query"]
    ast_score = result["ast_score"]
    
    if ground_truth["search_query"]:
        queries_with_search.append(ast_score)
    if ground_truth["integer_property_filter"]:
        queries_with_int_filter.append(ast_score)
    if ground_truth["text_property_filter"]:
        queries_with_text_filter.append(ast_score)
    if ground_truth["boolean_property_filter"]:
        queries_with_bool_filter.append(ast_score)
    if ground_truth["integer_property_aggregation"]:
        queries_with_int_agg.append(ast_score)
    if ground_truth["text_property_aggregation"]:
        queries_with_text_agg.append(ast_score)
    if ground_truth["boolean_property_aggregation"]:
        queries_with_bool_agg.append(ast_score)
    if ground_truth["groupby_property"]:
        queries_with_groupby.append(ast_score)

# Print component analysis
print("\nPer component analysis:")
if queries_with_search:
    print(f"Queries with search ({len(queries_with_search)}): {sum(queries_with_search)/len(queries_with_search):.2%}")
if queries_with_int_filter:
    print(f"Queries with integer filters ({len(queries_with_int_filter)}): {sum(queries_with_int_filter)/len(queries_with_int_filter):.2%}")
if queries_with_text_filter:
    print(f"Queries with text filters ({len(queries_with_text_filter)}): {sum(queries_with_text_filter)/len(queries_with_text_filter):.2%}")
if queries_with_bool_filter:
    print(f"Queries with boolean filters ({len(queries_with_bool_filter)}): {sum(queries_with_bool_filter)/len(queries_with_bool_filter):.2%}")
if queries_with_int_agg:
    print(f"Queries with integer aggregations ({len(queries_with_int_agg)}): {sum(queries_with_int_agg)/len(queries_with_int_agg):.2%}")
if queries_with_text_agg:
    print(f"Queries with text aggregations ({len(queries_with_text_agg)}): {sum(queries_with_text_agg)/len(queries_with_text_agg):.2%}")
if queries_with_bool_agg:
    print(f"Queries with boolean aggregations ({len(queries_with_bool_agg)}): {sum(queries_with_bool_agg)/len(queries_with_bool_agg):.2%}")
if queries_with_groupby:
    print(f"Queries with groupby ({len(queries_with_groupby)}): {sum(queries_with_groupby)/len(queries_with_groupby):.2%}")
