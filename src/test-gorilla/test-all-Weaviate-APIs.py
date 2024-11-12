from src.models import WeaviateQuery
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
from src.utils.weaviate_fc_utils import get_collections_info, build_weaviate_query_tool
from src.lm.lm import LMService
from pydantic import BaseModel
from typing import Optional, Any
import json

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

with open("../../data/synthetic-weaviate-queries.json", "r") as json_file:
    weaviate_queries_raw = json.load(json_file)
    weaviate_queries = []
    
    for query in weaviate_queries_raw:
        # Create filter objects if they exist
        int_filter = IntPropertyFilter(**query["integer_property_filter"]) if query["integer_property_filter"] else None
        text_filter = TextPropertyFilter(**query["text_property_filter"]) if query["text_property_filter"] else None
        bool_filter = BooleanPropertyFilter(**query["boolean_property_filter"]) if query["boolean_property_filter"] else None
        
        # Create aggregation objects if they exist
        int_agg = IntAggregation(**query["integer_property_aggregation"]) if query["integer_property_aggregation"] else None
        text_agg = TextAggregation(**query["text_property_aggregation"]) if query["text_property_aggregation"] else None
        bool_agg = BooleanAggregation(**query["boolean_property_aggregation"]) if query["boolean_property_aggregation"] else None

        # Create WeaviateQuery object
        weaviate_query = WeaviateQuery(
            target_collection=query["target_collection"],
            search_query=query["search_query"],
            integer_property_filter=int_filter,
            text_property_filter=text_filter,
            boolean_property_filter=bool_filter,
            integer_property_aggregation=int_agg,
            text_property_aggregation=text_agg,
            boolean_property_aggregation=bool_agg,
            groupby_property=query["groupby_property"],
            corresponding_natural_language_query=query["corresponding_natural_language_query"]
        )
        weaviate_queries.append(weaviate_query)

pretty_print_weaviate_query(weaviate_queries[0])

def abstract_syntax_tree_match_score(
        predicted_apis: WeaviateQuery,
        ground_truth: WeaviateQuery
    ) -> float:
    """
    Calculate a matching score between predicted and ground truth WeaviateQuery objects.
    Returns a float between 0.0 and 1.0, where 1.0 indicates a perfect match.
    """
    score = 0.0
    
    # Weight definitions for different components
    weights = {
        'target_collection': 0.15,
        'search_query': 0.1,
        'filters': 0.25,
        'aggregations': 0.25,
        'groupby': 0.1,
        'natural_language': 0.15
    }
    
    # Check target collection match (exact match required)
    if predicted_apis.target_collection == ground_truth.target_collection:
        score += weights['target_collection']
    
    # Check search query match (if both have search queries)
    if predicted_apis.search_query and ground_truth.search_query:
        if predicted_apis.search_query.lower() == ground_truth.search_query.lower():
            score += weights['search_query']
    elif predicted_apis.search_query is None and ground_truth.search_query is None:
        score += weights['search_query']  # Both None is also a match
    
    # Check filters match
    filter_score = 0.0
    filter_count = 0
    
    # Integer filter check
    if predicted_apis.integer_property_filter is None and ground_truth.integer_property_filter is None:
        filter_score += 1
        filter_count += 1
    elif predicted_apis.integer_property_filter and ground_truth.integer_property_filter:
        if (predicted_apis.integer_property_filter.property_name == ground_truth.integer_property_filter.property_name and
            predicted_apis.integer_property_filter.operator == ground_truth.integer_property_filter.operator and
            predicted_apis.integer_property_filter.value == ground_truth.integer_property_filter.value):
            filter_score += 1
        filter_count += 1
        
    # Text filter check
    if predicted_apis.text_property_filter is None and ground_truth.text_property_filter is None:
        filter_score += 1
        filter_count += 1
    elif predicted_apis.text_property_filter and ground_truth.text_property_filter:
        if (predicted_apis.text_property_filter.property_name == ground_truth.text_property_filter.property_name and
            predicted_apis.text_property_filter.operator == ground_truth.text_property_filter.operator and
            predicted_apis.text_property_filter.value == ground_truth.text_property_filter.value):
            filter_score += 1
        filter_count += 1
        
    # Boolean filter check
    if predicted_apis.boolean_property_filter is None and ground_truth.boolean_property_filter is None:
        filter_score += 1
        filter_count += 1
    elif predicted_apis.boolean_property_filter and ground_truth.boolean_property_filter:
        if (predicted_apis.boolean_property_filter.property_name == ground_truth.boolean_property_filter.property_name and
            predicted_apis.boolean_property_filter.operator == ground_truth.boolean_property_filter.operator and
            predicted_apis.boolean_property_filter.value == ground_truth.boolean_property_filter.value):
            filter_score += 1
        filter_count += 1
    
    if filter_count > 0:
        score += weights['filters'] * (filter_score / filter_count)
    
    # Check aggregations match
    agg_score = 0.0
    agg_count = 0
    
    # Integer aggregation check
    if predicted_apis.integer_property_aggregation is None and ground_truth.integer_property_aggregation is None:
        agg_score += 1
        agg_count += 1
    elif predicted_apis.integer_property_aggregation and ground_truth.integer_property_aggregation:
        if (predicted_apis.integer_property_aggregation.property_name == ground_truth.integer_property_aggregation.property_name and
            predicted_apis.integer_property_aggregation.metrics == ground_truth.integer_property_aggregation.metrics):
            agg_score += 1
        agg_count += 1
        
    # Text aggregation check
    if predicted_apis.text_property_aggregation is None and ground_truth.text_property_aggregation is None:
        agg_score += 1
        agg_count += 1
    elif predicted_apis.text_property_aggregation and ground_truth.text_property_aggregation:
        if (predicted_apis.text_property_aggregation.property_name == ground_truth.text_property_aggregation.property_name and
            predicted_apis.text_property_aggregation.metrics == ground_truth.text_property_aggregation.metrics):
            agg_score += 1
        agg_count += 1
        
    # Boolean aggregation check
    if predicted_apis.boolean_property_aggregation is None and ground_truth.boolean_property_aggregation is None:
        agg_score += 1
        agg_count += 1
    elif predicted_apis.boolean_property_aggregation and ground_truth.boolean_property_aggregation:
        if (predicted_apis.boolean_property_aggregation.property_name == ground_truth.boolean_property_aggregation.property_name and
            predicted_apis.boolean_property_aggregation.metrics == ground_truth.boolean_property_aggregation.metrics):
            agg_score += 1
        agg_count += 1
    
    if agg_count > 0:
        score += weights['aggregations'] * (agg_score / agg_count)
    
    # Check groupby match
    if predicted_apis.groupby_property == ground_truth.groupby_property:
        score += weights['groupby']
    
    # Check natural language query match
    if predicted_apis.corresponding_natural_language_query.lower() == ground_truth.corresponding_natural_language_query.lower():
        score += weights['natural_language']
    
    return score

print("\033[96m\nAbstract Syntax Tree Score between the first and last query:\033[0m")
print(abstract_syntax_tree_match_score(
    weaviate_queries[0],
    weaviate_queries[300]
)) # 0.6

print("\033[96m\nAbstract Syntax Tree Score between the first and second query:\033[0m")
print(abstract_syntax_tree_match_score(
    weaviate_queries[0],
    weaviate_queries[1]
)) # 0.75

print("\033[96m\nEquivalence Relation:\033[0m")
print(abstract_syntax_tree_match_score(
    weaviate_queries[0],
    weaviate_queries[0]
)) # 1.0

openai_api_key = ""

lm_service = LMService(
    model_provider = "openai",
    model_name = "gpt-4o",
    api_key = openai_api_key
)

print(f"Running AST test for {len(weaviate_queries)} queries.") # 64 for 6 schemas

with open("../../data/cleaned-simple-3-collection-schemas.json", "r") as json_file:
    database_schemas = json.load(json_file)

database_schemas = [json.loads(schema) if isinstance(schema, str) else schema for schema in database_schemas]

print("Database Schema:\n")
print(database_schemas[1])
print(f"Total Database Schemas: {len(database_schemas)}")
print(weaviate_queries[64])

database_schema_index = 0

import weaviate
import requests

weaviate_client = weaviate.connect_to_local()
url = "http://localhost:8080/v1/schema"

weaviate_client.collections.delete_all()

# init db with database_schemas[0]

for class_schema in database_schemas[0]["weaviate_collections"]:
    clean_schema = {
        'class': class_schema['class'],  # Use existing 'class' field
        'description': class_schema.get('description', ''),
        'properties': [
            {
                'name': prop['name'],
                'description': prop.get('description', ''),
                'dataType': prop['data_type']  # Weaviate expects dataType, not data_type
            }
            for prop in class_schema.get('properties', [])
        ],
        'vectorizer': class_schema.get('vectorizer', 'text2vec-transformers'),
        'vectorIndexType': class_schema.get('vectorIndexType', 'hnsw'),
    }

    schema_str = json.dumps(clean_schema)
    response = requests.post(
        url=url,
        data=schema_str,
        headers={'Content-Type': 'application/json'}
    )

    print(f"Response status: {response.status_code}")

# Init Weaviate Tool

for idx, query in enumerate(weaviate_queries):
    if idx > 0 and idx % 64 == 0:
        # Change DB Collections
        database_schema_index += 1
        weaviate_client.collections.delete_all()
        for class_schema in database_schemas[database_schema_index]["weaviate_collections"]:
            clean_schema = {
                'class': class_schema['class'],  # Use existing 'class' field
                'description': class_schema.get('description', ''),
                'properties': [
                    {
                        'name': prop['name'],
                        'description': prop.get('description', ''),
                        'dataType': prop['data_type']  # Weaviate expects dataType, not data_type
                    }
                    for prop in class_schema.get('properties', [])
                ],
                'vectorizer': class_schema.get('vectorizer', 'text2vec-transformers'),
                'vectorIndexType': class_schema.get('vectorIndexType', 'hnsw'),
            }

            schema_str = json.dumps(clean_schema)
            response = requests.post(
                url=url,
                data=schema_str,
                headers={'Content-Type': 'application/json'}
            )

            print(f"Response status: {response.status_code}")

            # build new Weaviate Tool


    nl_query = query.corresponding_natural_language_query
    print(nl_query)

    '''
    response = lm_service.one_step_function_selection_test(
        prompt=nl_query,
        tools=tools
    ).choices[0].message
    
    print(response)
    '''

weaviate_client.close()
