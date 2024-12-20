# TODO: Move model classes (QueryPredictionResult, ExperimentSummary) to src/models/experiment.py
from src.models import WeaviateQueryWithSchema, WeaviateQuery, QueryPredictionResult, ExperimentSummary
from src.models import (
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation,
    GroupBy
)
from src.models import Tool, Function, Parameters, ParameterProperty
from src.models import ResponseOrToolCalls
from src.utils.weaviate_fc_utils import (
    get_collections_info 
)
from src.utils.tool_with_rationale import (
    build_weaviate_query_tool_for_openai_with_rationale
)
from src.lm.lm import LMService
from src.utils.util import pretty_print_weaviate_query
from src.utils.load_queries import load_queries
from src.utils.metrics import abstract_syntax_tree_match_score
from pydantic import BaseModel
from typing import Optional, Any, List, Dict
import json
from datetime import datetime

print("\033[92m=== Starting Experiment Execution ===\033[0m")
print("\033[92m=== Loading Weaviate Queries ===\033[0m")

weaviate_queries = load_queries("../../data/synthetic-weaviate-queries-with-schemas.json")

print("\033[92m=== Initializing LM Service ===\033[0m")

# Configuration

MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-4o"
generate_with_models = True

api_key = ""

# add ollama
lm_service = LMService(
    model_provider = MODEL_PROVIDER,
    model_name = MODEL_NAME,
    api_key = api_key
)

print("\033[92m=== Loading Database Schemas ===\033[0m")

import weaviate
import requests

print("\033[92m=== Connecting to Weaviate ===\033[0m")
weaviate_client = weaviate.connect_to_local()
url = "http://localhost:8080/v1/schema"

# Initialize experiment results
detailed_results = []
per_schema_scores = {}
successful_predictions = 0
failed_predictions = 0
database_schema_index = 0
total_ast_score = 0  # Track total AST score

# Clean up, don't build the first schema outside of the experiment loop...
print("\033[92m=== Initializing First Schema ===\033[0m")

# Initialize first schema
weaviate_client.collections.delete_all()

# Use the database schema from the first query
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
if lm_service.model_provider == "openai":
    tools = [build_weaviate_query_tool_for_openai_with_rationale(
        collections_description=collections_description,
        collections_list=collections_enum,
        generate_with_models=generate_with_models)]
else:
    raise ValueError(f"{lm_service.model_provider} not supported for tool rationale ablation testing.")

print("\033[92m=== Starting Query Processing ===\033[0m")

# execute experiment
for idx, query in enumerate(weaviate_queries):
    print(f"\n\033[92m=== Processing Query {idx+1}/{len(weaviate_queries)} ===\033[0m")
    
    if idx > 0 and idx % 64 == 0:
        # Update per-schema scores
        per_schema_scores[database_schema_index] = sum(r.ast_score for r in detailed_results[-64:]) / 64
        print(f"\033[92mUpdated scores for schema {database_schema_index}: {per_schema_scores[database_schema_index]:.3f}\033[0m")
        
        # Change DB Collections
        database_schema_index += 1
        print(f"\033[92m=== Switching to Schema {database_schema_index} ===\033[0m")
        weaviate_client.collections.delete_all()
        
        # Use the database schema from the current query
        class_schemas = weaviate_queries[idx].database_schema.weaviate_collections
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
        if lm_service.model_provider == "openai":
            tools = [build_weaviate_query_tool_for_openai_with_rationale(
                collections_description=collections_description,
                collections_list=collections_enum,
                generate_with_models=generate_with_models)]
        else:
            raise ValueError(f"{lm_service.model_provider} not supported for tool rationale ablation testing.")

    try:
        nl_query = query.corresponding_natural_language_query
        print(f"\033[92mProcessing natural language query:\033[0m {nl_query}")
        print("\033[96mGROUND TRUTH QUERY:\033[0m")
        pretty_print_weaviate_query(query)
        
        # This should be behind the `generate_with_models` flag

        response = lm_service.one_step_function_selection_test(
            prompt=nl_query,
            tools=tools,
            parallel_tool_calls=False
        )
        
        if not response:
            print("\033[93mNo tool called\033[0m")
            result = QueryPredictionResult(
                query_index=idx,
                database_schema_index=database_schema_index,
                natural_language_query=nl_query,
                ground_truth_query=query,
                predicted_query=None,
                tool_rationale="",
                ast_score=0.0,
                error="No tool called"
            )
            failed_predictions += 1
        else:
            tool_call_args = json.loads(response[0].function.arguments)


            if generate_with_models:
                # Parse response directly into models when generate_with_models is True
                integer_property_filter = IntPropertyFilter(**tool_call_args["integer_property_filter"]) if "integer_property_filter" in tool_call_args else None
                text_property_filter = TextPropertyFilter(**tool_call_args["text_property_filter"]) if "text_property_filter" in tool_call_args else None
                boolean_property_filter = BooleanPropertyFilter(**tool_call_args["boolean_property_filter"]) if "boolean_property_filter" in tool_call_args else None
                integer_property_aggregation = IntAggregation(**tool_call_args["integer_property_aggregation"]) if "integer_property_aggregation" in tool_call_args else None
                text_property_aggregation = TextAggregation(**tool_call_args["text_property_aggregation"]) if "text_property_aggregation" in tool_call_args else None
                boolean_property_aggregation = BooleanAggregation(**tool_call_args["boolean_property_aggregation"]) if "boolean_property_aggregation" in tool_call_args else None

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

            print("\033[96mPREDICTED QUERY:\033[0m")
            pretty_print_weaviate_query(predicted_query)
            print("\033[96m\nRationale for Predicted Query:\033[0m")
            print(tool_call_args.get("tool_rationale"))
            print()

            # Calculate AST score
            ast_score = abstract_syntax_tree_match_score(predicted_query, query)
            print(f"\033[92mAST score: {ast_score:.3f}\033[0m")
            
            result = QueryPredictionResult(
                query_index=idx,
                database_schema_index=database_schema_index,
                natural_language_query=nl_query,
                ground_truth_query=query,
                predicted_query=predicted_query,
                tool_rationale=tool_call_args.get("tool_rationale"),
                ast_score=ast_score,
                error=None
            )
            successful_predictions += 1
            
    except Exception as e:
        print(f"\033[91mError occurred: {str(e)}\033[0m")
        result = QueryPredictionResult(
            query_index=idx,
            database_schema_index=database_schema_index,
            natural_language_query=nl_query,
            ground_truth_query=query,
            predicted_query=None,
            ast_score=0.0,
            tool_rationale="",
            error=str(e)
        )
        failed_predictions += 1
    
    detailed_results.append(result)
    total_ast_score += result.ast_score
    current_avg_ast_score = total_ast_score / (idx + 1)
    print(f"\033[92mProcessed query {idx+1}/{len(weaviate_queries)}, AST score: {result.ast_score}, Running Average AST Score: {current_avg_ast_score:.3f}\033[0m")

# Update scores for final schema
per_schema_scores[database_schema_index] = sum(r.ast_score for r in detailed_results[-64:]) / 64

print("\033[92m=== Creating Experiment Summary ===\033[0m")
# Create experiment summary
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
# Save results
with open(f"{MODEL_NAME}-experiment_results{'-with-models' if generate_with_models else ''}.json", "w") as f:
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