from lm import LMService, VectorizerService
from models import SimpleSyntheticSchema, ComplexSyntheticSchema
from create import CreateObjects

lm_service = LMService(
    model_provider = "openai",
    model_name = "gpt-4o",
    api_key = "sk-foobar"
)

vectorizer_service = VectorizerService(
    model_provider = "openai",
    model_name = "",
    api_key = "sk-foobar"
)

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