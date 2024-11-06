from src.lm.lm import LMService
from src.vectorizer.vectorizer import VectorizerService
from src.models import Property, WeaviateCollectionConfig, WeaviateCollections 
from src.models import SimpleSyntheticSchema, ComplexSyntheticSchema
from src.create.create import CreateObjects

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

use_case_overview_example = """This bookstore database system consists of three interconnected collections - Books, Authors, and Customers. 
The Books collection tracks inventory with titles, prices and availability. The Authors collection maintains author profiles with their names, 
total book sales, and active publishing status. The Customers collection manages customer data including names, loyalty points, and premium membership status. 
Together, these collections enable personalized recommendations, author performance tracking, and targeted customer engagement."""

schema_references = [
    WeaviateCollectionConfig(
        name="Books",
        properties=[
            Property(name="title", data_type=["TEXT"], description="The title of the book"),
            Property(name="price", data_type=["NUMBER"], description="The retail price of the book in dollars"),
            Property(name="is_available", data_type=["BOOLEAN"], description="Whether the book is currently in stock")
        ],
        envisioned_use_case_overview="Track book inventory, enable search by title, manage pricing, and monitor availability"
    ),
    WeaviateCollectionConfig(
        name="Authors", 
        properties=[
            Property(name="name", data_type=["TEXT"], description="The full name of the author"),
            Property(name="total_sales", data_type=["NUMBER"], description="Total number of books sold by this author"),
            Property(name="is_active", data_type=["BOOLEAN"], description="Whether the author is currently publishing new works")
        ],
        envisioned_use_case_overview="Manage author profiles, track sales performance, and monitor active publishing status"
    ),
    WeaviateCollectionConfig(
        name="Customers",
        properties=[
            Property(name="name", data_type=["TEXT"], description="The full name of the customer"),
            Property(name="loyalty_points", data_type=["NUMBER"], description="Number of loyalty points accumulated by the customer"),
            Property(name="is_premium", data_type=["BOOLEAN"], description="Whether the customer has premium membership status")
        ],
        envisioned_use_case_overview="Track customer information, manage loyalty program, and identify premium members"
    )
]

schemas = []
related_schemas = CreateObjects(
    num_samples=50,
    task_instructions=f"""
    Generate 3 synthetic database collection schemas for a business domain of your choice (e.g. restaurant, hospital, school etc).

    For reference, here is an example of 3 related collections for a bookstore:
    {use_case_overview_example}

    IMPORTANT!! Your schema should:
    1. Be for a DIFFERENT business domain than the example
    2. Have exactly 3 collections that work together
    3. Each collection must have exactly:
    - 1 TEXT property (for things like names/titles/descriptions)
    - 1 NUMBER property (for things like quantities/metrics/scores) 
    - 1 BOOLEAN property (for things like flags/statuses)
    4. Include a brief overview explaining how the collections work together

    The collections should have meaningful relationships and support common business operations in your chosen domain.

    IMPORTANT!! Do not include any spaces in collection names. If you want to use something like Travel Agency, please camel case it such as: `TravelAgency`.
    """,
    output_model=WeaviateCollections,
    lm_service=lm_service,
    vectorizer_service=vectorizer_service,
    dedup_strategy="last_k",
    dedup_params={}
)
schemas.extend(related_schemas)

import json
with open("./data/simple-3-collection-schemas.json", "w+") as file:
    json.dump(schemas, file, indent=4)