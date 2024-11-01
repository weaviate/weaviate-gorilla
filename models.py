from pydantic import BaseModel, field_validator

class CollectionRouterQuery(BaseModel):
    database_schema: dict
    gold_collection: str 
    synthetic_query: str

class SyntheticQuery(BaseModel):
    query: str

class SyntheticSingleAPIQuery(BaseModel):
    query: str
    explanation: str
    api_reference: str

# Note Multi-Hop might have a hierarchical structure to it...
class SyntheticMultiAPIQuery(BaseModel):
    query: str
    explanation: str
    api_references: list[str]

class Property(BaseModel):
    name: str
    data_type: list[str]
    description: str

class WeaviateCollectionConfig(BaseModel):
    name: str
    properties: list[Property]
    envisioned_use_case_overview: str

class WeaviateCollections(BaseModel):
    weaviate_collections: list[WeaviateCollectionConfig]

class SimpleSyntheticSchema(BaseModel):
    envisioned_use_case_description: str
    name: str
    text_valued_property_name: str
    int_valued_property_name: str
    boolean_valued_property_name: str

# Not sure if this works
class ComplexSyntheticSchema(BaseModel):
    envisioned_use_case_description: str
    name: str
    text_valued_property_names: list[str]
    int_valued_property_names: list[str]
    boolean_valued_property_names: list[str]

    @field_validator('text_valued_property_names', 'int_valued_property_names', 'boolean_valued_property_names')
    def check_list_length(cls, v):
         assert len(v) == 2, f'Must have at least two {v}'
         return v

class PredictionWithGroundTruth(BaseModel):
    prediction: int
    ground_truth: int

class PromptWithResponse(BaseModel):
    prompt: str
    response: str

class FunctionClassifierTestResult(BaseModel):
    num_correct: int
    num_attempted: int
    accuracy: float
    confusion_matrix: list[PredictionWithGroundTruth]
    misclassified_repsonses: list[PromptWithResponse]
    all_responses: list[PromptWithResponse]

class TestLMConnectionModel(BaseModel):
    generic_response: str
