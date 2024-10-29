from lm import LMService
from vectorizer import VectorizerService
from models import Property, WeaviateCollectionConfig, SimpleSyntheticSchema, ComplexSyntheticSchema
from create import CreateObjects

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

use_case_overview_example = "By combining these properties, the bookstore can develop a cohesive AI-driven solution. Customers receive smart recommendations based on title similarities, dynamic pricing strategies powered by price insights, and accurate real-time information on is_available status. This integration ensures efficient inventory management, enhances customer satisfaction, and optimizes sales by leveraging the strengths of each property."

simple_schema_reference = WeaviateCollectionConfig(
    name="BookStore",
    properties=[
        Property(
            name="title",
            data_type="TEXT"
        ),
        Property(
            name="price",
            data_type="NUMBER"
        ),
        Property(
            name="is_available",
            data_type="BOOLEAN"
        )
    ],
    envisioned_use_case_overview=use_case_overview_example
)


schemas = CreateObjects(
    num_samples = 50,
    task_instructions = f"""
    Generate a synthetic database schema.
    Here is an example: {simple_schema_reference}
    With example use case: {use_case_overview_example}

    IMPORTANT!! Please ensure the synthetic schema has exactly 1 TEXT property, 1 NUMBER property, and 1 BOOLEAN property.
    """,
    output_model=WeaviateCollectionConfig,
    lm_service=lm_service,
    vectorizer_service=vectorizer_service,
    dedup_strategy="brute_force",
    dedup_params={}
)
import json
with open("./data/simple-synthetic-schemas.json", "w+") as file:
    json.dump(schemas, file, indent=4)