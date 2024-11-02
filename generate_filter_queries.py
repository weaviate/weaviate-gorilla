from models import SyntheticQuery
from create import CreateObjects
from lm import LMService
from vectorizer import VectorizerService
import json

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


# Load schemas from JSON
with open("simple-3-collection-schemas.json", "r") as json_file:
    database_schemas = json.load(json_file)

# Define APIs
search_apis = [
    "Semantic search through a collection"
]

filter_apis = [
    "Filter by an integer-valued property such as =, >, <, >=, or <=",
    "Filter by a text-valued property such as =, CONTAINS",
    "Filter by a boolean-valued property such as ="
]

aggregate_apis = [
    "Aggregate an integer-valued property",
    "Aggregate a text-valued property",
    "Aggregate a boolean-valued property",
    "Count objects"
]

# Combine all APIs
all_apis = search_apis + filter_apis + aggregate_apis

# Prepare the prompt template
create_single_hop_query_prompt = """
Given a user's database schema and an API reference, write a natural language command simulating a case when the user would want to use the API.

[[ database schema ]]
{database_schema}

[[ API reference ]]
{api_reference}

[[ natural language command ]]
"""

def format_schema(schema):
    # Format the schema for inclusion in the prompt
    return json.dumps(schema, indent=2)

synthetic_queries = []

for database_schema in database_schemas:
    for api_reference in all_apis:
        # Prepare the task instructions
        task_instructions = create_single_hop_query_prompt.format(
            database_schema=format_schema(database_schema),
            api_reference=api_reference
        )
        
        # Generate the synthetic query
        queries = CreateObjects(
            num_samples=1,
            task_instructions=task_instructions,
            output_model=SyntheticQuery,
            lm_service=lm_service,
            vectorizer_service=vectorizer_service,
            dedup_strategy="none"  # No deduplication needed for single samples
        )
        
        # Append queries with associated metadata
        for query in queries:
            synthetic_queries.append({
                "database_schema": database_schema,
                "api_reference": api_reference,
                "synthetic_query": query
            })

# Save the synthetic queries to a file
with open("synthetic_queries.json", "w") as file:
    json.dump(synthetic_queries, file, indent=4)
