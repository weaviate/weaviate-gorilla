import json
from src.create.create import CreateObjects
from src.lm.lm import LMService
from src.vectorizer.vectorizer import VectorizerService
from src.models import WeaviateQuery
from src.generate_queries.api_descriptions import (
    search,
    int_property_filter,
    text_property_filter,
    boolean_property_filter,
    int_property_aggregation,
    text_property_aggregation,
    boolean_property_aggregation,
    groupby
)

searches = [search, ""]
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

with open("./data/simple-3-collection-schemas.json", "r") as json_file:
    database_schemas = json.load(json_file)

def format_schema(schema):
    return json.dumps(schema, indent=2)

for database_schema in database_schemas:
    task_instructions = create_query_prompt.format(
        database_schema=format_schema(database_schema)
    )
    query = CreateObjects(
        num_samples=1,
        task_instructions=task_instructions,
        output_model=WeaviateQuery,
        reference_objects=[searches, filters, aggregations, groupbys]
        lm_service=LMService,
        vectorizer_service=VectorizerService,
        dedup_strategy="none"
    )[0]
    print(query)

    # append query

# save file