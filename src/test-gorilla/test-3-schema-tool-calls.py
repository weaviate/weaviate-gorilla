import os
import json
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel
from src.models import (
    WeaviateQuery,
    QueryPredictionResult, 
    ExperimentSummary,
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation,
    GroupBy,
    ResponseOrToolCalls
)
from src.utils.load_queries import load_queries
from src.utils.metrics import abstract_syntax_tree_match_score
from src.utils.weaviate_fc_utils import (
    get_collections_info,
    build_weaviate_query_tool_for_openai
)
from src.utils.tool_per_collection import build_one_tool_per_collection
from src.utils.util import pretty_print_weaviate_query
from src.lm.lm import LMService
import weaviate

# Configuration
MODEL_NAME = "gpt-4"
api_key = ""
generate_with_models = True

print("\033[92m=== Starting Tool-Per-Collection vs Single-Tool Test ===\033[0m")

print("\033[92m=== Loading Weaviate Queries ===\033[0m")
weaviate_queries = load_queries("../../data/synthetic-weaviate-queries-with-schemas.json")

print("\033[92m=== Initializing LM Services ===\033[0m")
lm_service = LMService(
    model_provider="openai",
    model_name=MODEL_NAME,
    api_key=api_key
)

print("\033[92m=== Connecting to Weaviate ===\033[0m")
weaviate_client = weaviate.connect_to_local()
url = "http://localhost:8080/v1/schema"

print("\033[92m=== Initializing First Schema ===\033[0m")
weaviate_client.collections.delete_all()

# Initialize variables for experiment results
single_tool_results = []
multi_tool_results = []
per_schema_scores_single = {}
per_schema_scores_multi = {}
database_schema_index = 0

# Load first schema
class_schemas = weaviate_queries[0].database_schema.weaviate_collections
for class_schema in class_schemas:
    schema_dict = {
        'class': class_schema.name,
        'description': class_schema.envisioned_use_case_overview,
        'properties': []
    }
    for prop in class_schema.properties:
        schema_dict['properties'].append({
            'name': prop.name,
            'description': prop.description,
            'dataType': prop.data_type
        })
    schema_dict['vectorizer'] = 'text2vec-transformers'
    schema_dict['vectorIndexType'] = 'hnsw'

    schema_str = json.dumps(schema_dict)
    response = requests.post(
        url=url,
        data=schema_str,
        headers={'Content-Type': 'application/json'}
    )
    print(f"\033[92mCreated collection: {schema_dict['class']}\033[0m")

collections_description, collections_enum = get_collections_info(weaviate_client)

multi_tools = build_one_tool_per_collection(
    collections_description=collections_description,
    collections_list=collections_enum,
    generate_with_models=generate_with_models
)

print("\033[92m=== Starting Query Processing ===\033[0m")

for idx, query in enumerate(weaviate_queries):
    print(f"\n\033[92m=== Processing Query {idx+1}/{len(weaviate_queries)} ===\033[0m")
    
    # Switch schema every 64 queries if needed
    if idx > 0 and idx % 64 == 0:
        # Update per-schema scores
        last_64_single = single_tool_results[-64:]
        last_64_multi = multi_tool_results[-64:]
        
        if last_64_single:
            per_schema_scores_single[database_schema_index] = sum(r.ast_score for r in last_64_single) / 64
        if last_64_multi:
            per_schema_scores_multi[database_schema_index] = sum(r.ast_score for r in last_64_multi) / 64
            
        print(f"\033[92mSchema {database_schema_index} scores:\033[0m")
        print(f"Single tool: {per_schema_scores_single[database_schema_index]:.3f}")
        print(f"Multi tool: {per_schema_scores_multi[database_schema_index]:.3f}")

        database_schema_index += 1
        print(f"\033[92m=== Switching to Schema {database_schema_index} ===\033[0m")
        weaviate_client.collections.delete_all()
        
        # Use the database schema from the current query
        class_schemas = query.database_schema.weaviate_collections
        for class_schema in class_schemas:
            schema_dict = {
                'class': class_schema.name,
                'description': class_schema.envisioned_use_case_overview,
                'properties': []
            }
            for prop in class_schema.properties:
                schema_dict['properties'].append({
                    'name': prop.name,
                    'description': prop.description,
                    'dataType': prop.data_type
                })
            schema_dict['vectorizer'] = 'text2vec-transformers'
            schema_dict['vectorIndexType'] = 'hnsw'

            schema_str = json.dumps(schema_dict)
            response = requests.post(
                url=url,
                data=schema_str,
                headers={'Content-Type': 'application/json'}
            )
            print(f"\033[92mCreated collection: {schema_dict['class']}\033[0m")

        collections_description, collections_enum = get_collections_info(weaviate_client)

        multi_tools = build_one_tool_per_collection(
            collections_description=collections_description,
            collections_list=collections_enum,
            generate_with_models=generate_with_models
        )

    nl_query = query.corresponding_natural_language_query
    print(f"\033[92mProcessing natural language query:\033[0m {nl_query}")
    print("\033[96mGROUND TRUTH QUERY:\033[0m")
    pretty_print_weaviate_query(query)

    # Test with multiple tools
    try:
        multi_response = lm_service.one_step_function_selection_test(
            prompt=nl_query,
            tools=multi_tools
        )
        
        if not multi_response:
            multi_result = QueryPredictionResult(
                query_index=idx,
                database_schema_index=database_schema_index,
                natural_language_query=nl_query,
                ground_truth_query=query,
                predicted_query=None,
                ast_score=0.0,
                error="No response"
            )
        else:
            tool_call = multi_response[0]
            tool_call_args = tool_call.arguments.model_dump()
            
            # Build predicted query from tool call
            predicted_query = WeaviateQuery(
                target_collection=tool_call_args["collection_name"],
                search_query=tool_call_args.get("search_query"),
                integer_property_filter=IntPropertyFilter(**tool_call_args["integer_property_filter"]) if tool_call_args.get("integer_property_filter") else None,
                text_property_filter=TextPropertyFilter(**tool_call_args["text_property_filter"]) if tool_call_args.get("text_property_filter") else None,
                boolean_property_filter=BooleanPropertyFilter(**tool_call_args["boolean_property_filter"]) if tool_call_args.get("boolean_property_filter") else None,
                integer_property_aggregation=IntAggregation(**tool_call_args["integer_property_aggregation"]) if tool_call_args.get("integer_property_aggregation") else None,
                text_property_aggregation=TextAggregation(**tool_call_args["text_property_aggregation"]) if tool_call_args.get("text_property_aggregation") else None,
                boolean_property_aggregation=BooleanAggregation(**tool_call_args["boolean_property_aggregation"]) if tool_call_args.get("boolean_property_aggregation") else None,
                groupby_property=tool_call_args.get("groupby_property"),
                corresponding_natural_language_query=nl_query
            )
            
            ast_score = abstract_syntax_tree_match_score(predicted_query, query)
            multi_result = QueryPredictionResult(
                query_index=idx,
                database_schema_index=database_schema_index,
                natural_language_query=nl_query,
                ground_truth_query=query,
                predicted_query=predicted_query,
                ast_score=ast_score,
                error=None
            )
            
    except Exception as e:
        multi_result = QueryPredictionResult(
            query_index=idx,
            database_schema_index=database_schema_index,
            natural_language_query=nl_query,
            ground_truth_query=query,
            predicted_query=None,
            ast_score=0.0,
            error=str(e)
        )

    single_tool_results.append(single_result)
    multi_tool_results.append(multi_result)
    
    print(f"\033[92mSingle Tool AST Score: {single_result.ast_score:.3f}\033[0m")
    print(f"\033[92mMulti Tool AST Score: {multi_result.ast_score:.3f}\033[0m")

# Update scores for final schema
last_64_single = single_tool_results[-64:] if len(single_tool_results) > 64 else single_tool_results
last_64_multi = multi_tool_results[-64:] if len(multi_tool_results) > 64 else multi_tool_results

if last_64_single:
    per_schema_scores_single[database_schema_index] = sum(r.ast_score for r in last_64_single) / len(last_64_single)
if last_64_multi:
    per_schema_scores_multi[database_schema_index] = sum(r.ast_score for r in last_64_multi) / len(last_64_multi)

print("\033[92m=== Creating Experiment Summaries ===\033[0m")

single_tool_summary = ExperimentSummary(
    timestamp=datetime.now().isoformat(),
    model_name=f"{MODEL_NAME}-single-tool",
    generate_with_models=generate_with_models,
    total_queries=len(weaviate_queries),
    successful_predictions=sum(1 for r in single_tool_results if r.predicted_query is not None),
    failed_predictions=sum(1 for r in single_tool_results if r.predicted_query is None),
    average_ast_score=sum(r.ast_score for r in single_tool_results) / len(single_tool_results),
    per_schema_scores=per_schema_scores_single,
    detailed_results=single_tool_results
)

multi_tool_summary = ExperimentSummary(
    timestamp=datetime.now().isoformat(),
    model_name=f"{MODEL_NAME}-multi-tool",
    generate_with_models=generate_with_models,
    total_queries=len(weaviate_queries),
    successful_predictions=sum(1 for r in multi_tool_results if r.predicted_query is not None),
    failed_predictions=sum(1 for r in multi_tool_results if r.predicted_query is None),
    average_ast_score=sum(r.ast_score for r in multi_tool_results) / len(multi_tool_results),
    per_schema_scores=per_schema_scores_multi,
    detailed_results=multi_tool_results
)

print("\033[92m=== Saving Results ===\033[0m")
with open(f"{MODEL_NAME}-single-tool-test{'-with-models' if generate_with_models else ''}.json", "w") as f:
    f.write(single_tool_summary.model_dump_json(indent=2))

with open(f"{MODEL_NAME}-multi-tool-test{'-with-models' if generate_with_models else ''}.json", "w") as f:
    f.write(multi_tool_summary.model_dump_json(indent=2))

print("\n\033[92mSingle Tool Summary:\033[0m")
print(f"Total Queries: {single_tool_summary.total_queries}")
print(f"Successful Predictions: {single_tool_summary.successful_predictions}")
print(f"Failed Predictions: {single_tool_summary.failed_predictions}")
print(f"Average AST Score: {single_tool_summary.average_ast_score:.3f}")

print("\n\033[92mMulti Tool Summary:\033[0m")
print(f"Total Queries: {multi_tool_summary.total_queries}")
print(f"Successful Predictions: {multi_tool_summary.successful_predictions}")
print(f"Failed Predictions: {multi_tool_summary.failed_predictions}")
print(f"Average AST Score: {multi_tool_summary.average_ast_score:.3f}")

print("\n\033[92mPer-Schema Scores:\033[0m")
for schema_idx in per_schema_scores_single.keys():
    print(f"Schema {schema_idx}:")
    print(f"  Single Tool: {per_schema_scores_single[schema_idx]:.3f}")
    print(f"  Multi Tool:  {per_schema_scores_multi[schema_idx]:.3f}")

print("\033[92m=== Closing Weaviate Client ===\033[0m")
weaviate_client.close()
