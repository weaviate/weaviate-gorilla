import json
from src.create.create import CreateObjects
from src.lm.lm import LMService
from src.vectorizer.vectorizer import VectorizerService
from src.models import WeaviateQuery
from src.generate_queries.api_descriptions import (
    search_query,
    int_property_filter,
    text_property_filter,
    boolean_property_filter,
    int_property_aggregation,
    text_property_aggregation,
    boolean_property_aggregation,
    groupby
)

searches = [search_query, ""]
filters = [int_property_filter, text_property_filter, boolean_property_filter, ""]
aggregations = [int_property_aggregation, text_property_aggregation, boolean_property_aggregation, ""]
groupbys = [groupby, ""]

openai_api_key = ""

lm_service = LMService(
    model_provider = "openai",
    model_name = "gpt-4o",
    api_key = openai_api_key
)

lm_service.connection_test()

vectorizer_service = VectorizerService(
    model_provider = "openai",
    model_name = "text-embedding-3-small",
    api_key = openai_api_key
)

vectorizer_service.connection_test()

# This isn't perfect, but the query operators are populated in the `references` loop internal to `CreateObjects`
create_query_prompt = """
Given a user's database schema write a natural language commands simulating cases where the user would want to use the provided query operators.

[[ database schema ]]
{database_schema}

[[ query operators that should be used in the query ]]
"""

with open("../../data/simple-3-collection-schemas.json", "r") as json_file:
    database_schemas = json.load(json_file)

def format_schema(schema):
    return json.dumps(schema, indent=2)

weaviate_queries = []

import time
start = time.time()

for idx, database_schema in enumerate(database_schemas):
    print(f"\n\033[1mRunning for {time.time() - start} seconds.\033[0m\n")
    print(f"\033[96mWriting queries for database {idx+1}:\033[0m")
    print(f"{database_schema}\n\n")
    task_instructions = create_query_prompt.format(
        database_schema=format_schema(database_schema)
    )
    queries = CreateObjects(
        num_samples=1,
        task_instructions=task_instructions,
        output_model=WeaviateQuery,
        reference_objects=[searches, filters, aggregations, groupbys],
        lm_service=lm_service,
        vectorizer_service=vectorizer_service,
        dedup_strategy="none"
    )
    print("\033[93mQueries generated for this schema:\033[0m")
    for query in queries:
        # Parse the JSON string into a dict if it's a string
        if isinstance(query, str):
            query_dict = json.loads(query)
        else:
            query_dict = query
            
        query_obj = WeaviateQuery(**query_dict)
        print(f"\033[93m{query_obj}\033[0m")
        weaviate_queries.append(query_dict)

    print(f"\n\033[92mCreated {len(weaviate_queries)} Gorilla queries.\033[0m\n")

# Save the synthetic queries to a file
with open("synthetic-weaviate-queries.json", "w") as file:
    json.dump(weaviate_queries, file, indent=4)