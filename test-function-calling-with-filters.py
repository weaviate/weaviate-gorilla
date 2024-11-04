from models import QueryWithFilter, IntPropertyFilter, TextPropertyFilter, BooleanPropertyFilter
from models import Tool, Function, Parameters, ParameterProperty
from weaviate_fc_utils import get_collections_info
from lm import LMService
from pydantic import BaseModel
from typing import Optional, Any

import json
import requests
import time

class FilterQueryResult(BaseModel):
    query: str
    database_schema: dict
    metadata: str
    property_name: str 
    operator: str
    value: Any
    predicted_filter: Optional[str]
    is_correct: bool

class ExperimentResults(BaseModel):
    total_queries: int
    correct_predictions: int
    accuracy: float
    results: list[FilterQueryResult]

# Load synthetic filter queries generated by generate-filter-queries.py
with open("./data/synthetic-filter-queries.json", "r") as json_file:
    filter_queries_raw = json.load(json_file)
    filter_queries = []
    for query in filter_queries_raw:
        # Parse database schema from string back to dict if needed
        database_schema = query["database_schema"]
        if isinstance(database_schema, str):
            database_schema = json.loads(database_schema)
            
        # Create the appropriate filter object based on metadata
        if query["metadata"] == "INT PROPERTY FILTER":
            filter_obj = IntPropertyFilter(
                property_name=query["property_name"],
                operator=query["operator"],
                value=int(query["value"])
            )
        elif query["metadata"] == "TEXT PROPERTY FILTER":
            filter_obj = TextPropertyFilter(
                property_name=query["property_name"], 
                operator=query["operator"],
                value=query["value"]
            )
        elif query["metadata"] == "BOOLEAN PROPERTY FILTER":
            filter_obj = BooleanPropertyFilter(
                property_name=query["property_name"],
                operator=query["operator"], 
                value=bool(query["value"])
            )
            
        # Create QueryWithFilter object
        filter_queries.append(
            QueryWithFilter(
                database_schema=database_schema,
                gold_collection=database_schema["weaviate_collections"][0]["name"],
                gold_filter=filter_obj,
                synthetic_query=query["query"]
            )
        )

# Weaviate Function Calling Setup

import weaviate
weaviate_client = weaviate.connect_to_local()
url = "http://localhost:8080/v1/schema"

openai_api_key = ""

lm_service = LMService(
    model_provider = "openai",
    model_name = "gpt-4o",
    api_key = openai_api_key
)

correct_counter = 0
experiment_results = []

for idx, filter_query in enumerate(filter_queries):
    # Reset collections currently defined in the Weaviate instance
    weaviate_client.collections.delete_all()
    
    # Get schema and create collections with a post requests to Weaviate
    class_schemas = filter_query.database_schema["weaviate_collections"]
    for class_schema in class_schemas:
        clean_schema = {
            'class': class_schema['name'],  # Use existing 'class' field
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
        schema_str = json.dumps(clean_schema) # Note, this shouldn't be necessary, but oh well
        requests.post(
            url,
            data=schema_str,
            headers={'Content-Type': 'application/json'}
        )

    time.sleep(10) # give Weaviate 10 seconds to create the collections

    # build function from schemas
    collections_description, collections_list = get_collections_info(weaviate_client)

    # Create tool with `collections_list`
    tools = [Tool(
        type="function",
        function=Function(
            name="search_weaviate_collection",
            description="Search for the most relevant items to the provided `search_query` in a Weaviate Database Collection.",
            parameters=Parameters(
                type="object",
                properties={
                    "collection_name": ParameterProperty(
                        type="string",
                        description=f"The Weaviate Collection to search through. More detailed information about the particular collections in this database: {collections_description}",
                        enum=collections_list
                    ),
                    "search_query": ParameterProperty(
                        type="string",
                        description="The search query."
                    ),
                    "filter_string": ParameterProperty(
                        type="string",
                        description="""
                        Filter expression using prefix notation to ensure unambiguous order of operations.
                        
                        Basic condition syntax: property_name:operator:value
                        
                        Compound expressions use prefix AND/OR with parentheses:
                        - AND(condition1, condition2)
                        - OR(condition1, condition2)
                        - AND(condition1, OR(condition2, condition3))
                        
                        Examples:
                        - Simple: age:>:25
                        - Compound: AND(age:>:25, price:<:1000)
                        - Complex: OR(AND(age:>:25, price:<:1000), category:=:'electronics')
                        - Nested: AND(status:=:'active', OR(price:<:50, AND(rating:>:4, stock:>:100)))
                        
                        Supported operators:
                        - Comparison: =, >, <, >=, <= 
                        - Text: LIKE, CONTAINS
                        """
                    )
                },
                required=["collection_name"]
            )
        )
    )]

    prompt = "Answer the question. Use the provided tools to gain additional context."
    prompt += f"\nuser query: {filter_query.synthetic_query}"

    response = lm_service.one_step_function_selection_test(
        prompt=prompt,
        tools=tools
    ).choices[0].message

    print("\033[96m\nTesting with query:\033[0m")
    print(filter_query.synthetic_query)
    print("\033[96mGold collection:\033[0m")
    print(filter_query.gold_collection)

    predicted_collection = None
    is_correct = False
    
    if "tool_calls" in response.model_dump().keys():
        print("\033[96mLLM-selected collection:\033[0m")
        print(len(response.tool_calls)) # save this somewhere
        for tool_call in response.tool_calls:
            arguments_json = json.loads(tool_call.function.arguments)
            print("\033[92mALL ARGUMENTS SELECTED\n\033[0m")
            print(arguments_json)
            predicted_collection = arguments_json["collection_name"]
            print(predicted_collection)
            if predicted_collection == filter_query.gold_collection:
                correct_counter += 1
                is_correct = True
                print(f"\033[92mSuccess! Current success rate: {(correct_counter / (idx + 1)) * 100}\033[0m")
                break # stop looping through these tool_calls (it might call the same correct collection with 2 or more queries, etc.)
    else:
        print("\033[96mThe LLM didn't call a function.\033[0m")

    result = FilterQueryResult(
        query=filter_query.synthetic_query,
        database_schema=filter_query.database_schema,
        metadata=query["metadata"],
        property_name=query["property_name"],
        operator=query["operator"],
        value=query["value"],
        predicted_filter=predicted_collection,
        is_correct=is_correct
    )
    experiment_results.append(result)

final_results = ExperimentResults(
    total_queries=len(experiment_results),
    correct_predictions=correct_counter,
    accuracy=correct_counter / len(experiment_results) if experiment_results else 0,
    results=experiment_results
)

# Save results to JSON file
with open("filter-query-results.json", "w") as f:
    json.dump(final_results.model_dump(), f, indent=2)

weaviate_client.close()