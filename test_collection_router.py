from models import CollectionRouterQuery
from models import Tool, Function, Parameters, ParameterProperty
from weaviate_fc_utils import get_collections_info
from lm import LMService

import json

with open("./data/collection-routing-queries.json", "r") as json_file:
    collection_router_queries_raw = json.load(json_file)
    collection_router_queries = [CollectionRouterQuery(**query) for query in collection_router_queries_raw]

print(collection_router_queries[0])

# Weaviate Function Calling Setup

import weaviate
weaviate_client = weaviate.connect_to_local()

openai_api_key = ""

lm_service = LMService(
    model_provider = "openai",
    model_name = "gpt-4o",
    api_key = openai_api_key
)

prompt = "Answer the question. Use the provided tools to gain additional context."

for collection_router_query in collection_router_queries:
    weaviate_client.collections.delete_all()
    schema = collection_router_query.database_schema
    # create schemas with post request from schema

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
                        description="The Weaviate Collection to search through.",
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

    function_selected = lm_service.one_step_function_selection_test(
        prompt=prompt,
        tools=tools
    )

    print(function_selected)
    break

    # parse tool






    