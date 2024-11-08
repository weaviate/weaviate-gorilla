from api_descriptions import (
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

# load databases

# for database_schema in databases

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