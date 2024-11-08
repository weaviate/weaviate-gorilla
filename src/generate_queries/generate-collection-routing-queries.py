import json
from src.create.create import CreateObjects
from src.models import SyntheticQuery, CollectionRouterQuery
from src.lm.lm import LMService
from src.vectorizer.vectorizer import VectorizerService

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
with open("./data/simple-3-collection-schemas.json", "r") as json_file:
    database_schemas = json.load(json_file)

# Prepare the prompt template
create_query_prompt = """
Given the following database collection schema, write a natural language semantic search query that a user might ask to find relevant items in this collection.

The query should be a conceptual search phrase that could match semantically related items, rather than an exact property match. For example, if searching a book collection, queries like "adventures in space" or "medieval fantasy stories" would be good semantic searches.

[[ Collection Schema ]]
{collection_schema}

[[ Semantic Search Query ]]
Write a natural, conversational query that focuses on concepts and topics rather than exact matches:
"""

def format_collection_schema(collection):
    # Format the collection schema for inclusion in the prompt
    return json.dumps(collection, indent=2)

synthetic_queries = []

for database_schema in database_schemas:
    database_schema = json.loads(database_schema)
    weaviate_collections = database_schema.get('weaviate_collections', [])
    for collection in weaviate_collections:
        # Prepare the task instructions
        task_instructions = create_query_prompt.format(
            collection_schema=format_collection_schema(collection)
        )
        
        # Generate the synthetic query
        synthetic_query = CreateObjects(
            num_samples=1,
            task_instructions=task_instructions,
            output_model=SyntheticQuery,  # Since the output is a simple string
            lm_service=lm_service,
            vectorizer_service=vectorizer_service,
            dedup_strategy="none"
        )[0] # only one sample
        print("\033[32mCreated synthetic query for the collection:\n\033[0m")
        print(collection)
        print("\033[32mSynthetic query:\n\033[0m")
        print(synthetic_query)

        # Append queries with associated metadata using Pydantic model
        synthetic_queries.append(
            CollectionRouterQuery(
                database_schema=database_schema,
                gold_collection=collection['name'],
                synthetic_query=synthetic_query.query
            ).model_dump()
        )

# Save the synthetic queries to a file
with open("synthetic_queries.json", "w") as file:
    json.dump(synthetic_queries, file, indent=4)
