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
    build_weaviate_query_tool, 
    _build_weaviate_filter_return_model,
    _build_weaviate_aggregation_return_model
)
from src.lm.lm import LMService
from pydantic import BaseModel
from typing import Optional, Any, List, Dict
import json
from datetime import datetime

print("\033[92m=== Starting Program Execution ===\033[0m")

# TODO: Move pretty printing utilities to src/utils/printing.py
def pretty_print_weaviate_query(query: WeaviateQuery) -> None:
    """Pretty prints a WeaviateQuery object with color and indentation."""
    print("\n\033[92mWeaviate Query Details:\033[0m")
    print(f"  \033[92mTarget Collection:\033[0m {query.target_collection}")
    print(f"  \033[92mSearch Query:\033[0m {query.search_query}")
    
    if query.integer_property_filter:
        print("  \033[92mInteger Filter:\033[0m")
        print(f"    Property: {query.integer_property_filter.property_name}")
        print(f"    Operator: {query.integer_property_filter.operator}")
        print(f"    Value: {query.integer_property_filter.value}")
    
    if query.text_property_filter:
        print("  \033[92mText Filter:\033[0m")
        print(f"    Property: {query.text_property_filter.property_name}")
        print(f"    Operator: {query.text_property_filter.operator}")
        print(f"    Value: {query.text_property_filter.value}")
        
    if query.boolean_property_filter:
        print("  \033[92mBoolean Filter:\033[0m")
        print(f"    Property: {query.boolean_property_filter.property_name}")
        print(f"    Operator: {query.boolean_property_filter.operator}")
        print(f"    Value: {query.boolean_property_filter.value}")
        
    if query.integer_property_aggregation:
        print("  \033[92mInteger Aggregation:\033[0m")
        print(f"    Property: {query.integer_property_aggregation.property_name}")
        print(f"    Metrics: {query.integer_property_aggregation.metrics}")
        
    if query.text_property_aggregation:
        print("  \033[92mText Aggregation:\033[0m")
        print(f"    Property: {query.text_property_aggregation.property_name}")
        print(f"    Metrics: {query.text_property_aggregation.metrics}")
        
    if query.boolean_property_aggregation:
        print("  \033[92mBoolean Aggregation:\033[0m")
        print(f"    Property: {query.boolean_property_aggregation.property_name}")
        print(f"    Metrics: {query.boolean_property_aggregation.metrics}")
        
    if query.groupby_property:
        print(f"  \033[92mGroup By:\033[0m {query.groupby_property}")
        
    print(f"  \033[92mNatural Language Query:\033[0m {query.corresponding_natural_language_query}")

print("\033[92m=== Loading Weaviate Queries ===\033[0m")

# TODO: Move query loading and processing logic to src/data/query_loader.py
with open("../../data/synthetic-weaviate-queries-with-schemas.json", "r") as json_file:
    weaviate_queries_raw = json.load(json_file)
    print(f"\033[92mLoaded {len(weaviate_queries_raw)} raw queries\033[0m")
    weaviate_queries = []
    database_schemas = []
    
    for query_idx, query_data in enumerate(weaviate_queries_raw):
        print(f"\033[92mProcessing query {query_idx + 1}\033[0m")
        query = query_data["query"]
        database_schema = query_data["database_schema"]
        
        # Create filter objects if they exist
        int_filter = None
        if query["integer_property_filter"]:
            print(f"\033[92mProcessing integer filter for query {query_idx + 1}\033[0m")
            int_filter_data = query["integer_property_filter"].copy()
            if int_filter_data["property_name"]:  # Check if property_name exists and is not empty
                int_filter_data["property_name"] = int_filter_data["property_name"][0].lower() + int_filter_data["property_name"][1:]
            int_filter = IntPropertyFilter(**int_filter_data)
            
        text_filter = None
        if query["text_property_filter"]:
            print(f"\033[92mProcessing text filter for query {query_idx + 1}\033[0m")
            text_filter_data = query["text_property_filter"].copy()
            if text_filter_data["property_name"]:  # Check if property_name exists and is not empty
                text_filter_data["property_name"] = text_filter_data["property_name"][0].lower() + text_filter_data["property_name"][1:]
            text_filter = TextPropertyFilter(**text_filter_data)
            
        bool_filter = None
        if query["boolean_property_filter"]:
            print(f"\033[92mProcessing boolean filter for query {query_idx + 1}\033[0m")
            bool_filter_data = query["boolean_property_filter"].copy()
            if bool_filter_data["property_name"]:  # Check if property_name exists and is not empty
                bool_filter_data["property_name"] = bool_filter_data["property_name"][0].lower() + bool_filter_data["property_name"][1:]
            bool_filter = BooleanPropertyFilter(**bool_filter_data)
        
        # Create aggregation objects if they exist
        int_agg = None
        if query["integer_property_aggregation"]:
            print(f"\033[92mProcessing integer aggregation for query {query_idx + 1}\033[0m")
            int_agg_data = query["integer_property_aggregation"].copy()
            if int_agg_data["property_name"]:  # Check if property_name exists and is not empty
                int_agg_data["property_name"] = int_agg_data["property_name"][0].lower() + int_agg_data["property_name"][1:]
            int_agg = IntAggregation(**int_agg_data)
            
        text_agg = None
        if query["text_property_aggregation"]:
            print(f"\033[92mProcessing text aggregation for query {query_idx + 1}\033[0m")
            text_agg_data = query["text_property_aggregation"].copy()
            if text_agg_data["property_name"]:  # Check if property_name exists and is not empty
                text_agg_data["property_name"] = text_agg_data["property_name"][0].lower() + text_agg_data["property_name"][1:]
            text_agg = TextAggregation(**text_agg_data)
            
        bool_agg = None
        if query["boolean_property_aggregation"]:
            print(f"\033[92mProcessing boolean aggregation for query {query_idx + 1}\033[0m")
            bool_agg_data = query["boolean_property_aggregation"].copy()
            if bool_agg_data["property_name"]:  # Check if property_name exists and is not empty
                bool_agg_data["property_name"] = bool_agg_data["property_name"][0].lower() + bool_agg_data["property_name"][1:]
            bool_agg = BooleanAggregation(**bool_agg_data)

        # Create WeaviateQueryWithSchema object
        print(f"\033[92mCreating WeaviateQueryWithSchema object for query {query_idx + 1}\033[0m")
        
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
        print(f"\033[92mSuccessfully processed query {query_idx + 1}\033[0m")

# TODO: Move AST matching logic to src/evaluation/ast_matcher.py
def abstract_syntax_tree_match_score(
        predicted_apis: WeaviateQuery,
        ground_truth: WeaviateQueryWithSchema
    ) -> float:
    """
    Calculate a matching score between predicted and ground truth WeaviateQuery objects.
    Returns a float between 0.0 and 1.0, where 1.0 indicates a perfect match.
    """
    print("\033[92m=== Calculating AST Match Score ===\033[0m")
    score = 0.0
    
    # Weight definitions for different components
    weights = {
        'target_collection': 0.2,
        'search_query': 0.2,
        'filters': 0.2,
        'aggregations': 0.2,
        'groupby': 0.2
    }
    
    # Check target collection match (exact match required)
    print(f"\033[92mComparing target collections:\033[0m")
    print(f"Predicted: {predicted_apis.target_collection}")
    print(f"Ground Truth: {ground_truth.target_collection}")
    if predicted_apis.target_collection == ground_truth.target_collection:
        score += weights['target_collection']
        print(f"\033[92mTarget collection match! Score: +{weights['target_collection']}\033[0m")
    
    # Check search query match (if both have search queries)
    print(f"\033[92mComparing search queries:\033[0m")
    print(f"Predicted: {predicted_apis.search_query}")
    print(f"Ground Truth: {ground_truth.search_query}")
    if predicted_apis.search_query and ground_truth.search_query:
        if predicted_apis.search_query.lower() == ground_truth.search_query.lower():
            score += weights['search_query']
            print(f"\033[92mSearch query match! Score: +{weights['search_query']}\033[0m")
    elif predicted_apis.search_query is None and ground_truth.search_query is None:
        score += weights['search_query']  # Both None is also a match
        print(f"\033[92mBoth search queries are None! Score: +{weights['search_query']}\033[0m")
    
    # Check filters match
    print("\033[92m=== Checking Filters ===\033[0m")
    filter_score = 0.0
    filter_count = 0
    
    # Integer filter check
    if predicted_apis.integer_property_filter is None and ground_truth.integer_property_filter is None:
        filter_score += 1
        filter_count += 1
        print("\033[92mBoth integer filters are None - match!\033[0m")
    elif predicted_apis.integer_property_filter and ground_truth.integer_property_filter:
        if (predicted_apis.integer_property_filter.property_name == ground_truth.integer_property_filter.property_name and
            predicted_apis.integer_property_filter.operator == ground_truth.integer_property_filter.operator and
            predicted_apis.integer_property_filter.value == ground_truth.integer_property_filter.value):
            filter_score += 1
            print("\033[92mInteger filters match!\033[0m")
        filter_count += 1
        
    # Text filter check
    if predicted_apis.text_property_filter is None and ground_truth.text_property_filter is None:
        filter_score += 1
        filter_count += 1
        print("\033[92mBoth text filters are None - match!\033[0m")
    elif predicted_apis.text_property_filter and ground_truth.text_property_filter:
        if (predicted_apis.text_property_filter.property_name == ground_truth.text_property_filter.property_name and
            predicted_apis.text_property_filter.operator == ground_truth.text_property_filter.operator and
            predicted_apis.text_property_filter.value == ground_truth.text_property_filter.value):
            filter_score += 1
            print("\033[92mText filters match!\033[0m")
        filter_count += 1
        
    # Boolean filter check
    if predicted_apis.boolean_property_filter is None and ground_truth.boolean_property_filter is None:
        filter_score += 1
        filter_count += 1
        print("\033[92mBoth boolean filters are None - match!\033[0m")
    elif predicted_apis.boolean_property_filter and ground_truth.boolean_property_filter:
        if (predicted_apis.boolean_property_filter.property_name == ground_truth.boolean_property_filter.property_name and
            predicted_apis.boolean_property_filter.operator == ground_truth.boolean_property_filter.operator and
            predicted_apis.boolean_property_filter.value == ground_truth.boolean_property_filter.value):
            filter_score += 1
            print("\033[92mBoolean filters match!\033[0m")
        filter_count += 1
    
    if filter_count > 0:
        filter_contribution = weights['filters'] * (filter_score / filter_count)
        score += filter_contribution
        print(f"\033[92mFilter contribution to score: +{filter_contribution:.3f}\033[0m")
    
    # Check aggregations match
    print("\033[92m=== Checking Aggregations ===\033[0m")
    agg_score = 0.0
    agg_count = 0
    
    # Integer aggregation check
    if predicted_apis.integer_property_aggregation is None and ground_truth.integer_property_aggregation is None:
        agg_score += 1
        agg_count += 1
        print("\033[92mBoth integer aggregations are None - match!\033[0m")
    elif predicted_apis.integer_property_aggregation and ground_truth.integer_property_aggregation:
        if (predicted_apis.integer_property_aggregation.property_name == ground_truth.integer_property_aggregation.property_name and
            predicted_apis.integer_property_aggregation.metrics == ground_truth.integer_property_aggregation.metrics):
            agg_score += 1
            print("\033[92mInteger aggregations match!\033[0m")
        agg_count += 1
        
    # Text aggregation check
    if predicted_apis.text_property_aggregation is None and ground_truth.text_property_aggregation is None:
        agg_score += 1
        agg_count += 1
        print("\033[92mBoth text aggregations are None - match!\033[0m")
    elif predicted_apis.text_property_aggregation and ground_truth.text_property_aggregation:
        if (predicted_apis.text_property_aggregation.property_name == ground_truth.text_property_aggregation.property_name and
            predicted_apis.text_property_aggregation.metrics == ground_truth.text_property_aggregation.metrics):
            agg_score += 1
            print("\033[92mText aggregations match!\033[0m")
        agg_count += 1
        
    # Boolean aggregation check
    if predicted_apis.boolean_property_aggregation is None and ground_truth.boolean_property_aggregation is None:
        agg_score += 1
        agg_count += 1
        print("\033[92mBoth boolean aggregations are None - match!\033[0m")
    elif predicted_apis.boolean_property_aggregation and ground_truth.boolean_property_aggregation:
        if (predicted_apis.boolean_property_aggregation.property_name == ground_truth.boolean_property_aggregation.property_name and
            predicted_apis.boolean_property_aggregation.metrics == ground_truth.boolean_property_aggregation.metrics):
            agg_score += 1
            print("\033[92mBoolean aggregations match!\033[0m")
        agg_count += 1
    
    if agg_count > 0:
        agg_contribution = weights['aggregations'] * (agg_score / agg_count)
        score += agg_contribution
        print(f"\033[92mAggregation contribution to score: +{agg_contribution:.3f}\033[0m")
    
    # Check groupby match
    print("\033[92m=== Checking GroupBy ===\033[0m")
    print(f"Predicted GroupBy: {predicted_apis.groupby_property}")
    print(f"Ground Truth GroupBy: {ground_truth.groupby_property}")
    if predicted_apis.groupby_property == ground_truth.groupby_property:
        score += weights['groupby']
        print(f"\033[92mGroupBy match! Score: +{weights['groupby']}\033[0m")
    
    print(f"\033[92mFinal AST Match Score: {score:.3f}\033[0m")
    return score

openai_api_key = ""

print("\033[92m=== Initializing LM Service ===\033[0m")
lm_service = LMService(
    model_provider = "openai",
    model_name = "gpt-4o",
    api_key = openai_api_key
)

print("\033[92m=== Loading Database Schemas ===\033[0m")
# No need to load schemas separately since they're now included with queries

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

# TODO: Move schema initialization logic to src/database/schema_initializer.py
# Initialize first schema
weaviate_client.collections.delete_all()

# Use the database schema from the first query
class_schemas = weaviate_queries[0].database_schema.weaviate_collections
for class_schema in class_schemas:
    # Convert class_schema to dict format expected by Weaviate
    schema_dict = {
        'class': class_schema.name,
        'description': class_schema.envisioned_use_case_overview,
        'properties': []
    }
    
    # Add properties
    for prop in class_schema.properties:
        schema_dict['properties'].append({
            'name': prop.name,
            'description': prop.description,
            'dataType': prop.data_type
        })

    # Add vectorizer settings
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
tools = [build_weaviate_query_tool(collections_description=collections_description, collections_list=collections_enum)]

print("\033[92m=== Starting Query Processing ===\033[0m")

# TODO: Move experiment execution logic to src/experiment/executor.py
# Run experiment
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
            # Convert class_schema to dict format expected by Weaviate
            schema_dict = {
                'class': class_schema.name,
                'description': class_schema.envisioned_use_case_overview,
                'properties': []
            }
            
            # Add properties
            for prop in class_schema.properties:
                schema_dict['properties'].append({
                    'name': prop.name,
                    'description': prop.description,
                    'dataType': prop.data_type
                })

            # Add vectorizer settings
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
        tools = [build_weaviate_query_tool(collections_description=collections_description, collections_list=collections_enum)]

    try:
        nl_query = query.corresponding_natural_language_query
        print(f"\033[92mProcessing natural language query:\033[0m {nl_query}")
        response = lm_service.one_step_function_selection_test(
            prompt=nl_query,
            tools=tools
        ).choices[0].message
        
        if not response.tool_calls:
            print("\033[91mNo tool called.\033[0m")
            result = QueryPredictionResult(
                query_index=idx,
                database_schema_index=database_schema_index,
                natural_language_query=nl_query,
                ground_truth_query=query,
                predicted_query=None,
                ast_score=0.0,
                error="No functions selected"
            )
            failed_predictions += 1
        else:
            print("\033[92mParsing tool call response\033[0m")
            tool_call_args = json.loads(response.tool_calls[0].function.arguments)
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

            ast_score = abstract_syntax_tree_match_score(predicted_query, query)
            result = QueryPredictionResult(
                query_index=idx,
                database_schema_index=database_schema_index,
                natural_language_query=nl_query,
                ground_truth_query=query,
                predicted_query=predicted_query,
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
with open("gpt-4o-experiment_results.json", "w") as f:
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
