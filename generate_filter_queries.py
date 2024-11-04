from models import SyntheticFilterQueries
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

# Describe Filter DSL

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
