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
from src.utils.weaviate_fc_utils import (
    get_collections_info, 
    build_weaviate_query_tools, # Changed to plural
    build_weaviate_query_tool_for_ollama,
    _build_weaviate_filter_return_model,
    _build_weaviate_aggregation_return_model
)
from src.lm.lm import LMService
from src.utils.util import pretty_print_weaviate_query
from src.utils.metrics import abstract_syntax_tree_match_score
from pydantic import BaseModel
from typing import Optional, Any, List, Dict
import json
from datetime import datetime

# Number of predictions to generate per query for ensemble
NUM_PREDICTIONS = 1

print("\033[92m=== Starting Experiment Execution ===\033[0m")
print("\033[92m=== Loading Weaviate Queries ===\033[0m")

# could move to a `load_queries` helper
with open("../../data/synthetic-weaviate-queries-with-schemas.json", "r") as json_file:
    weaviate_queries_raw = json.load(json_file)
    print(f"\033[92mLoaded {len(weaviate_queries_raw)} raw queries\033[0m")
    weaviate_queries = []
    database_schemas = []
    
    for query_idx, query_data in enumerate(weaviate_queries_raw):
        query = query_data["query"]
        database_schema = query_data["database_schema"]
        
        # Create filter objects if they exist
        int_filter = None
        if query["integer_property_filter"]:
            int_filter_data = query["integer_property_filter"].copy()
            if int_filter_data["property_name"]:  # Check if property_name exists and is not empty
                int_filter_data["property_name"] = int_filter_data["property_name"][0].lower() + int_filter_data["property_name"][1:]
            int_filter = IntPropertyFilter(**int_filter_data)
            
        text_filter = None
        if query["text_property_filter"]:
            text_filter_data = query["text_property_filter"].copy()
            if text_filter_data["property_name"]:  # Check if property_name exists and is not empty
                text_filter_data["property_name"] = text_filter_data["property_name"][0].lower() + text_filter_data["property_name"][1:]
            text_filter = TextPropertyFilter(**text_filter_data)
            
        bool_filter = None
        if query["boolean_property_filter"]:
            bool_filter_data = query["boolean_property_filter"].copy()
            if bool_filter_data["property_name"]:  # Check if property_name exists and is not empty
                bool_filter_data["property_name"] = bool_filter_data["property_name"][0].lower() + bool_filter_data["property_name"][1:]
            bool_filter = BooleanPropertyFilter(**bool_filter_data)
        
        # Create aggregation objects if they exist
        int_agg = None
        if query["integer_property_aggregation"]:
            int_agg_data = query["integer_property_aggregation"].copy()
            if int_agg_data["property_name"]:  # Check if property_name exists and is not empty
                int_agg_data["property_name"] = int_agg_data["property_name"][0].lower() + int_agg_data["property_name"][1:]
            int_agg = IntAggregation(**int_agg_data)
            
        text_agg = None
        if query["text_property_aggregation"]:
            text_agg_data = query["text_property_aggregation"].copy()
            if text_agg_data["property_name"]:  # Check if property_name exists and is not empty
                text_agg_data["property_name"] = text_agg_data["property_name"][0].lower() + text_agg_data["property_name"][1:]
            text_agg = TextAggregation(**text_agg_data)
            
        bool_agg = None
        if query["boolean_property_aggregation"]:
            bool_agg_data = query["boolean_property_aggregation"].copy()
            if bool_agg_data["property_name"]:  # Check if property_name exists and is not empty
                bool_agg_data["property_name"] = bool_agg_data["property_name"][0].lower() + bool_agg_data["property_name"][1:]
            bool_agg = BooleanAggregation(**bool_agg_data)

        # Create WeaviateQueryWithSchema object
        
        # Convert database_schema string to dict if needed
        if isinstance(database_schema, str):
            database_schema = json.loads(database_schema)
            
        weaviate_query = WeaviateQueryWithSchema(
            target_collection=query["target_collection"],
            search_query=query["search_query"],
            integer_property_filter=int_filter,
            text_property_filter=text_filter,
            boolean_property_filter=bool_filter,
            integer_property_aggregation=int_agg,
            text_property_aggregation=text_agg,
            boolean_property_aggregation=bool_agg,
            groupby_property=query["groupby_property"][0].lower() + query["groupby_property"][1:] if query["groupby_property"] else None,
            corresponding_natural_language_query=query["corresponding_natural_language_query"],
            database_schema=database_schema
        )
        weaviate_queries.append(weaviate_query)


print("\033[92m=== Initializing LM Service ===\033[0m")

openai_api_key = ""
anthropic_api_key = ""

# add ollama
lm_service = LMService(
    model_provider = "openai",
    model_name = "gpt-4o",
    api_key = openai_api_key
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
if lm_service.model_provider == "ollama":
    tools = [build_weaviate_query_tool_for_ollama(
        collections_description=collections_description, 
        collections_list=collections_enum)]
else:
    tools = build_weaviate_query_tools(
        collections_description=collections_description, 
        collections_list=collections_enum, 
        num_tools=NUM_PREDICTIONS)

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
        if lm_service.model_provider == "ollama":
            tools = [build_weaviate_query_tool_for_ollama(collections_description=collections_description, collections_list=collections_enum)]
        else:
            tools = build_weaviate_query_tools(collections_description=collections_description, collections_list=collections_enum, num_tools=NUM_PREDICTIONS)

    try:
        nl_query = query.corresponding_natural_language_query
        print(f"\033[92mProcessing natural language query:\033[0m {nl_query}")
        
        # Generate multiple predictions and track the best one
        best_prediction = None
        best_ast_score = -1
        best_result = None
        
        print(f"\033[92mGenerating {NUM_PREDICTIONS} predictions for ensemble\033[0m")
        
        for pred_idx in range(NUM_PREDICTIONS):
            print(f"\033[92mGenerating prediction {pred_idx + 1}/{NUM_PREDICTIONS}\033[0m")
            
            response = lm_service.one_step_function_selection_test(
                prompt=nl_query,
                tools=[tools[pred_idx]] # Use different tool for each prediction
            )
            
            if not response:
                print(f"\033[93mNo tool called for prediction {pred_idx + 1}\033[0m")
                continue
                
            print(f"\033[92mParsing tool call response for prediction {pred_idx + 1}\033[0m")
            tool_call_args = response
            search_query = tool_call_args.get("search_query")
            
            filter_model = None
            if "filter_string" in tool_call_args:
                print(f"\033[92mProcessing filter string:\033[0m {tool_call_args['filter_string']}")
                filter_model = _build_weaviate_filter_return_model(tool_call_args["filter_string"])
            
            group_by_model = None
            metrics_model = None
            if "aggregation_string" in tool_call_args:
                print(f"\033[92mProcessing aggregation string:\033[0m {tool_call_args['aggregation_string']}")
                group_by_model, metrics_models = _build_weaviate_aggregation_return_model(tool_call_args["aggregation_string"])
                if metrics_models:
                    metrics_model = metrics_models[0]
            
            predicted_query = WeaviateQuery(
                target_collection=tool_call_args["collection_name"],
                search_query=search_query,
                integer_property_filter=filter_model if isinstance(filter_model, IntPropertyFilter) else None,
                text_property_filter=filter_model if isinstance(filter_model, TextPropertyFilter) else None,
                boolean_property_filter=filter_model if isinstance(filter_model, BooleanPropertyFilter) else None,
                integer_property_aggregation=metrics_model if isinstance(metrics_model, IntAggregation) else None,
                text_property_aggregation=metrics_model if isinstance(metrics_model, TextAggregation) else None,
                boolean_property_aggregation=metrics_model if isinstance(metrics_model, BooleanAggregation) else None,
                groupby_property=group_by_model,
                corresponding_natural_language_query=nl_query
            )

            # Calculate AST score for this prediction
            ast_score = abstract_syntax_tree_match_score(predicted_query, query)
            print(f"\033[92mPrediction {pred_idx + 1} AST score: {ast_score:.3f}\033[0m")
            
            # Update best prediction if this one is better
            if ast_score > best_ast_score:
                best_ast_score = ast_score
                best_prediction = predicted_query
                best_result = QueryPredictionResult(
                    query_index=idx,
                    database_schema_index=database_schema_index,
                    natural_language_query=nl_query,
                    ground_truth_query=query,
                    predicted_query=predicted_query,
                    ast_score=ast_score,
                    error=None
                )

        # After generating all predictions, use the best one
        if best_prediction:
            print(f"\033[92mUsing best prediction with AST score: {best_ast_score:.3f}\033[0m")
            result = best_result
            successful_predictions += 1
        else:
            print("\033[91mNo successful predictions in ensemble\033[0m")
            result = QueryPredictionResult(
                query_index=idx,
                database_schema_index=database_schema_index,
                natural_language_query=nl_query,
                ground_truth_query=query,
                predicted_query=None,
                ast_score=0.0,
                error="No successful predictions in ensemble"
            )
            failed_predictions += 1
            
    except Exception as e:
        print(f"\033[91mError occurred: {str(e)}\033[0m")
        result = QueryPredictionResult(
            query_index=idx,
            database_schema_index=database_schema_index,
            natural_language_query=nl_query,
            ground_truth_query=query,
            predicted_query=None,
            ast_score=0.0,
            error=str(e)
        )
        failed_predictions += 1
    
    detailed_results.append(result)
    total_ast_score += result.ast_score
    current_avg_ast_score = total_ast_score / (idx + 1)
    print(f"\033[92mProcessed query {idx+1}/{len(weaviate_queries)}, Best AST score: {result.ast_score}, Running Average AST Score: {current_avg_ast_score:.3f}\033[0m")

# Update scores for final schema
per_schema_scores[database_schema_index] = sum(r.ast_score for r in detailed_results[-64:]) / 64

print("\033[92m=== Creating Experiment Summary ===\033[0m")
# Create experiment summary
experiment_summary = ExperimentSummary(
    timestamp=datetime.now().isoformat(),
    model_name="gpt-4",
    total_queries=len(weaviate_queries),
    successful_predictions=successful_predictions,
    failed_predictions=failed_predictions,
    average_ast_score=sum(r.ast_score for r in detailed_results) / len(detailed_results),
    per_schema_scores=per_schema_scores,
    detailed_results=detailed_results
)

print("\033[92m=== Saving Results ===\033[0m")
# Save results
with open("claude-3-5-sonnet-experiment_results.json", "w") as f:
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