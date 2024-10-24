from lm import LMService
from vectorizer import VectorizerService
from models import SimpleSyntheticSchema, ComplexSyntheticSchema
from create import CreateObjects

openai_api_key = "sk-foobar"

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

schema_reference = "placeholder"
example_use_case = "placeholder"

schemas = CreateObjects(
    num_samples = 50,
    task_instructions = """
    Generate a synthetic database schema.
    Here is an example: {schema_reference}
    With example use case: {example_use case}
    """,
    output_model=SimpleSyntheticSchema
)

import json
with open("simple-synthetic-schemas.json", "w+"):
    json.dumps(schemas)