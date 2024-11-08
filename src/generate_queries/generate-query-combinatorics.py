import json
from src.create.create import CreateObjects
from src.lm.lm import LMService
from src.vectorizer.vectorizer import VectorizerService
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
groupby = [groupby, ""]

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

with open("./data/simple-3-collection-schemas.json", "r") as json_file:
    database_schemas = json.load(json_file)





def CreateObjects(
        num_samples: int,
        task_instructions: str, 
        output_model: BaseModel,
        lm_service: LMService,
        vectorizer_service: VectorizerService,
        reference_objects: list[list[str]] = None,
        dedup_strategy: str = "brute_force",
        dedup_params: dict = None
    ) -> list[dict]: