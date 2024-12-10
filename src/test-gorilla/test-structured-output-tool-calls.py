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
    build_weaviate_query_tool_for_ollama,
    build_weaviate_query_tool_for_openai,
    build_weaviate_query_tool_for_anthropic,
)
from src.utils.util import pretty_print_weaviate_query
from src.lm.lm import LMService
import weaviate

# Configuration
MODEL_PROVIDER = "openai"  # or "anthropic" or "ollama"
MODEL_NAME = "gpt-4o"
api_key = ""

generate_with_models = True

print("\033[92m=== Starting Structured Outputs Test ===\033[0m")

print("\033[92m=== Loading Weaviate Queries ===\033[0m")
weaviate_queries = load_queries("../../data/synthetic-weaviate-queries-with-schemas.json")

print("\033[92m=== Initializing LM Service ===\033[0m")
lm_service = LMService(
    model_provider=MODEL_PROVIDER,
    model_name=MODEL_NAME,
    api_key=api_key
)

print("\033[92m=== Connecting to Weaviate ===\033[0m")
weaviate_client = weaviate.connect_to_local()
url = "http://localhost:8080/v1/schema"

print("\033[92m=== Initializing First Schema ===\033[0m")
weaviate_client.collections.delete_all()

# Initialize variables for experiment results
detailed_results = []
per_schema_scores = {}
successful_predictions = 0
failed_predictions = 0
database_schema_index = 0
total_ast_score = 0.0

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

# Build tools based on model provider
if MODEL_PROVIDER == "ollama":
    tools = [build_weaviate_query_tool_for_ollama(
        collections_description=collections_description, 
        collections_list=collections_enum,
        generate_with_models=generate_with_models)]
    tools = [tool.model_dump() for tool in tools]
elif MODEL_PROVIDER == "openai":
    tools = [build_weaviate_query_tool_for_openai(
        collections_description=collections_description,
        collections_list=collections_enum,
        generate_with_models=generate_with_models)]
elif MODEL_PROVIDER == "anthropic":
    tools = [build_weaviate_query_tool_for_anthropic(
        collections_description=collections_description,
        collections_list=collections_enum,
        generate_with_models=generate_with_models)]
else:
    tools = []

print("\033[92m=== Starting Query Processing ===\033[0m")

for idx, query in enumerate(weaviate_queries):
    print(f"\n\033[92m=== Processing Query {idx+1}/{len(weaviate_queries)} ===\033[0m")
    
    # Switch schema every 64 queries if needed
    if idx > 0 and idx % 64 == 0:
        # Update per-schema scores
        last_64_results = detailed_results[-64:]
        if last_64_results:
            per_schema_scores[database_schema_index] = sum(r.ast_score for r in last_64_results) / 64
            print(f"\033[92mUpdated scores for schema {database_schema_index}: {per_schema_scores[database_schema_index]:.3f}\033[0m")

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
        
        # Rebuild tools for the new schema
        if MODEL_PROVIDER == "ollama":
            tools = [build_weaviate_query_tool_for_ollama(
                collections_description=collections_description,
                collections_list=collections_enum,
                generate_with_models=generate_with_models)]
            tools = [tool.model_dump() for tool in tools]
        elif MODEL_PROVIDER == "openai":
            tools = [build_weaviate_query_tool_for_openai(
                collections_description=collections_description,
                collections_list=collections_enum,
                generate_with_models=generate_with_models)]
        elif MODEL_PROVIDER == "anthropic":
            tools = [build_weaviate_query_tool_for_anthropic(
                collections_description=collections_description,
                collections_list=collections_enum,
                generate_with_models=generate_with_models)]
        else:
            tools = []

    nl_query = query.corresponding_natural_language_query
    print(f"\033[92mProcessing natural language query:\033[0m {nl_query}")
    print("\033[96mGROUND TRUTH QUERY:\033[0m")
    pretty_print_weaviate_query(query)

    try:
        # Call the LLM with structured outputs
        structured_response = lm_service.call_tools_with_structured_outputs(
            prompt=nl_query,
            tools=tools
        )

        if not structured_response:
            print("\033[93mNo structured response returned.\033[0m")
            result = QueryPredictionResult(
                query_index=idx,
                database_schema_index=database_schema_index,
                natural_language_query=nl_query,
                ground_truth_query=query,
                predicted_query=None,
                tool_rationale="",
                ast_score=0.0,
                error="No response"
            )
            failed_predictions += 1
        else:
            predicted_query = None
            if structured_response:
                # Assume a single tool call for simplicity
                tool_call = structured_response[0]
                tool_call_args = tool_call.arguments.model_dump()

                # Build typed filters/aggregations
                integer_property_filter = IntPropertyFilter(**tool_call_args["integer_property_filter"]) if tool_call_args.get("integer_property_filter") is not None else None
                text_property_filter = TextPropertyFilter(**tool_call_args["text_property_filter"]) if tool_call_args.get("text_property_filter") is not None else None
                boolean_property_filter = BooleanPropertyFilter(**tool_call_args["boolean_property_filter"]) if tool_call_args.get("boolean_property_filter") is not None else None
                integer_property_aggregation = IntAggregation(**tool_call_args["integer_property_aggregation"]) if tool_call_args.get("integer_property_aggregation") is not None else None
                text_property_aggregation = TextAggregation(**tool_call_args["text_property_aggregation"]) if tool_call_args.get("text_property_aggregation") is not None else None
                boolean_property_aggregation = BooleanAggregation(**tool_call_args["boolean_property_aggregation"]) if tool_call_args.get("boolean_property_aggregation") is not None else None

                predicted_query = WeaviateQuery(
                    target_collection=tool_call_args["collection_name"],
                    search_query=tool_call_args.get("search_query"),
                    integer_property_filter=integer_property_filter,
                    text_property_filter=text_property_filter,
                    boolean_property_filter=boolean_property_filter,
                    integer_property_aggregation=integer_property_aggregation,
                    text_property_aggregation=text_property_aggregation,
                    boolean_property_aggregation=boolean_property_aggregation,
                    groupby_property=tool_call_args.get("groupby_property"),
                    corresponding_natural_language_query=nl_query
                )
            else:
                # No tools called, just a response
                # predicted_query can be None here since we have no structured query
                print("\033[93mNo tools were used.\033[0m")

            if predicted_query:
                print("\033[96mPREDICTED QUERY:\033[0m")
                pretty_print_weaviate_query(predicted_query)
                ast_score = abstract_syntax_tree_match_score(predicted_query, query)
                print(f"\033[92mAST score: {ast_score:.3f}\033[0m")

                result = QueryPredictionResult(
                    query_index=idx,
                    database_schema_index=database_schema_index,
                    natural_language_query=nl_query,
                    ground_truth_query=query,
                    predicted_query=predicted_query,
                    tool_rationale="",
                    ast_score=ast_score,
                    error=None
                )
                successful_predictions += 1
            else:
                # No predicted query formed
                result = QueryPredictionResult(
                    query_index=idx,
                    database_schema_index=database_schema_index,
                    natural_language_query=nl_query,
                    ground_truth_query=query,
                    predicted_query=None,
                    tool_rationale="",
                    ast_score=0.0,
                    error="No query predicted"
                )
                failed_predictions += 1
            
        detailed_results.append(result)
        total_ast_score += result.ast_score
        current_avg_ast_score = total_ast_score / (idx + 1)
        print(f"\033[92mProcessed query {idx+1}/{len(weaviate_queries)}, AST score: {result.ast_score}, Running Average AST Score: {current_avg_ast_score:.3f}\033[0m")

    except Exception as e:
        print(f"\033[91mError occurred: {str(e)}\033[0m")
        result = QueryPredictionResult(
            query_index=idx,
            database_schema_index=database_schema_index,
            natural_language_query=nl_query,
            ground_truth_query=query,
            tool_rationale="",
            predicted_query=None,
            ast_score=0.0,
            error=str(e)
        )
        failed_predictions += 1
        detailed_results.append(result)
        total_ast_score += 0.0  # no change
        current_avg_ast_score = total_ast_score / (idx + 1)
        print(f"\033[92mProcessed query {idx+1}/{len(weaviate_queries)}, AST score: 0.000, Running Average AST Score: {current_avg_ast_score:.3f}\033[0m")

# Update scores for final schema
last_64_results = detailed_results[-64:] if len(detailed_results) > 64 else detailed_results
if last_64_results:
    per_schema_scores[database_schema_index] = sum(r.ast_score for r in last_64_results) / len(last_64_results)

print("\033[92m=== Creating Experiment Summary ===\033[0m")

experiment_summary = ExperimentSummary(
    timestamp=datetime.now().isoformat(),
    model_name=MODEL_NAME,
    total_queries=len(weaviate_queries),
    successful_predictions=successful_predictions,
    failed_predictions=failed_predictions,
    average_ast_score=sum(r.ast_score for r in detailed_results) / len(detailed_results),
    per_schema_scores=per_schema_scores,
    detailed_results=detailed_results,
    generate_with_models=generate_with_models
)

print("\033[92m=== Saving Results ===\033[0m")
with open(f"{MODEL_NAME}-structured-output-test{'-with-models' if generate_with_models else ''}.json", "w") as f:
    f.write(experiment_summary.model_dump_json(indent=2))

print("\n\033[92mExperiment Summary:\033[0m")
print(f"Total Queries: {experiment_summary.total_queries}")
print(f"Successful Predictions: {experiment_summary.successful_predictions}")
print(f"Failed Predictions: {experiment_summary.failed_predictions}")
print(f"Average AST Score: {experiment_summary.average_ast_score:.3f}")
print("\n\033[92mPer-Schema Scores:\033[0m")
for schema_idx, score in experiment_summary.per_schema_scores.items():
    print(f"Schema {schema_idx}: {score:.3f}")

print("\033[92m=== Closing Weaviate Client ===\033[0m")
weaviate_client.close()
