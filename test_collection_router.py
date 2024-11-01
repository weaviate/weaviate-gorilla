from models import CollectionRouterQuery
from weaviate_fc_utils import get_collections_info

import json

with open("./data/collection-routing-queries.json", "r") as json_file:
    collection_router_queries_raw = json.load(json_file)
    collection_router_queries = [CollectionRouterQuery(**query) for query in collection_router_queries_raw]

print(collection_router_queries[0])

# Weaviate Function Calling Setup

import weaviate
weaviate_client = weaviate.connect_to_local()

for collection_router_query in collection_router_queries:
    weaviate_client.collections.delete_all()
    schema = collection_router_query.database_schema
    # create schemas with post request from schema

    # build function from schemas
    collections_description, collections_list = get_collections_info(weaviate_client)

    #