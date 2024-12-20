from src.lm.lm import LMService
from src.vectorizer.vectorizer import VectorizerService
from src.models import Property, WeaviateCollectionConfig, WeaviateCollections 
from src.models import SimpleSyntheticSchema, ComplexSyntheticSchema
from src.create.create import CreateObjects
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

use_case_overview_example = """This bookstore database system consists of three interconnected collections - Books, Authors, and Reviews. 
The Books collection contains detailed book information including searchable book descriptions and synopses to help customers discover relevant titles. 
The Authors collection maintains author profiles with their detailed biographies that can be searched to find authors writing on specific topics or themes. 
The Reviews collection stores customer reviews with detailed text feedback that can be semantically searched to surface relevant customer experiences. 
Together, these collections enable rich content discovery, author background exploration, and review analysis."""

schema_references = [
    WeaviateCollectionConfig(
        name="Books",
        properties=[
            Property(name="title", data_type=["TEXT"], description="The title of the book"),
            Property(name="synopsis", data_type=["TEXT"], description="A detailed description of the book's content and plot that can be semantically searched"),
            Property(name="price", data_type=["NUMBER"], description="The retail price of the book in dollars"),
            Property(name="is_available", data_type=["BOOLEAN"], description="Whether the book is currently in stock")
        ],
        envisioned_use_case_overview="Enable rich book discovery through semantic search of synopses, manage pricing and inventory"
    ),
    WeaviateCollectionConfig(
        name="Authors", 
        properties=[
            Property(name="name", data_type=["TEXT"], description="The full name of the author"),
            Property(name="biography", data_type=["TEXT"], description="Detailed author biography that can be semantically searched"),
            Property(name="total_sales", data_type=["NUMBER"], description="Total number of books sold by this author"),
            Property(name="is_active", data_type=["BOOLEAN"], description="Whether the author is currently publishing new works")
        ],
        envisioned_use_case_overview="Enable author discovery through biography search, track sales performance, and monitor publishing status"
    ),
    WeaviateCollectionConfig(
        name="Reviews",
        properties=[
            Property(name="title", data_type=["TEXT"], description="The title of the review"),
            Property(name="content", data_type=["TEXT"], description="The detailed review text that can be semantically searched"),
            Property(name="rating", data_type=["NUMBER"], description="Numerical rating given in the review (1-5)"),
            Property(name="is_verified", data_type=["BOOLEAN"], description="Whether this is a verified purchase review")
        ],
        envisioned_use_case_overview="Enable semantic search across review content, analyze ratings, and highlight verified reviews"
    )
]

schemas = []
related_schemas = CreateObjects(
    num_samples=5,
    task_instructions=f"""
    Generate 3 synthetic database collection schemas for a business domain of your choice (e.g. restaurant, hospital, school etc).

    For reference, here is an example of 3 related collections for a bookstore:
    {use_case_overview_example}

    IMPORTANT!! Your schema should:
    1. Be for a DIFFERENT business domain than the example
    2. Have exactly 3 collections that work together
    3. Each collection must have exactly:
    - 2 TEXT properties (one for basic identification like name/title AND one for rich searchable content like description/details)
    - 1 NUMBER property (for things like quantities/metrics/scores) 
    - 1 BOOLEAN property (for things like flags/statuses)
    4. Include a brief overview explaining how the collections work together
    5. At least one TEXT property in each collection should contain rich content suitable for semantic search (like descriptions, overviews, or detailed text)

    The collections should have meaningful relationships and support common business operations in your chosen domain, with a focus on enabling rich semantic search capabilities.

    IMPORTANT!! Do not include any spaces in collection names. If you want to use something like Travel Agency, please camel case it such as: `TravelAgency`.
    """,
    output_model=WeaviateCollections,
    lm_service=lm_service,
    vectorizer_service=vectorizer_service,
    dedup_strategy="last_k",
    dedup_params={}
)

# Convert WeaviateCollections objects to dictionaries before extending
related_schemas_dicts = [schema.model_dump() if isinstance(schema, WeaviateCollections) else schema for schema in related_schemas]
schemas.extend(related_schemas_dicts)

print(type(schemas))
print("\n")
print(type(schemas[0]))

with open("3-collection-schemas-with-search-property.json", "w+") as file:
    json.dump(schemas, file, indent=4)

# serialize to markdown here in the future