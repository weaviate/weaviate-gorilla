from src.models import CollectionRouterQuery
from src.models import Tool, Function, Parameters, ParameterProperty
from src.utils.weaviate_fc_utils import get_collections_info
from src.lm.lm import LMService
from pydantic import BaseModel
from typing import Optional

import json
import requests
import time

class CollectionRoutingResult(BaseModel):
    query: str
    gold_collection: str
    predicted_collection: Optional[str]
    is_correct: bool
    
class ExperimentResults(BaseModel):
    total_queries: int
    correct_predictions: int
    accuracy: float
    results: list[CollectionRoutingResult]

with open("./data/collection-routing-queries.json", "r") as json_file:
    collection_router_queries_raw = json.load(json_file)
    collection_router_queries = [CollectionRouterQuery(**query) for query in collection_router_queries_raw]

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

for idx, collection_router_query in enumerate(collection_router_queries):
    # Reset collections currently defined in the Weaviate instance
    weaviate_client.collections.delete_all()
    
    # Get schema and create collections with a post requests to Weaviate
    class_schemas = collection_router_query.database_schema["weaviate_collections"]
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
                    )
                },
                required=["collection_name", "search_query"]
            )
        )
    )]

    prompt = "Answer the question. Use the provided tools to gain additional context."
    prompt += f"\nuser query: {collection_router_query.synthetic_query}"

    response = lm_service.one_step_function_selection_test(
        prompt=prompt,
        tools=tools
    ).choices[0].message

    print("\033[96m\nTesting with query:\033[0m")
    print(collection_router_query.synthetic_query)
    print("\033[96mGold collection:\033[0m")
    print(collection_router_query.gold_collection)

    predicted_collection = None
    is_correct = False
    
    if "tool_calls" in response.model_dump().keys():
        print("\033[96mLLM-selected collection:\033[0m")
        print(len(response.tool_calls)) # save this somewhere
        for tool_call in response.tool_calls:
            arguments_json = json.loads(tool_call.function.arguments)
            predicted_collection = arguments_json["collection_name"]
            print(predicted_collection)
            if predicted_collection == collection_router_query.gold_collection:
                correct_counter += 1
                is_correct = True
                print(f"\033[92mSuccess! Current success rate: {(correct_counter / (idx + 1)) * 100}\033[0m")
                break # stop looping through these tool_calls (it might call the same correct collection with 2 or more queries, etc.)
    else:
        print("\033[96mThe LLM didn't call a function.\033[0m")

    result = CollectionRoutingResult(
        query=collection_router_query.synthetic_query,
        gold_collection=collection_router_query.gold_collection,
        predicted_collection=predicted_collection,
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
with open("collection_routing_results_with_descriptions.json", "w") as f:
    json.dump(final_results.model_dump(), f, indent=2)

weaviate_client.close()