from pydantic import BaseModel, field_validator, Field
from typing import Literal, Optional, Dict, List, Union

# Note, this needs to be cleaned up

# Basic Property Filter Models
class IntPropertyFilter(BaseModel):
    property_name: str
    operator: Literal["=", "<", ">", "<=", ">="]
    value: int | float

class TextPropertyFilter(BaseModel):
    property_name: str
    operator: Literal["=", "LIKE"]
    value: str

class BooleanPropertyFilter(BaseModel):
    property_name: str
    operator: Literal["=", "!="]
    value: bool

# Basic Query Models
class CollectionRouterQuery(BaseModel):
    database_schema: dict
    gold_collection: str 
    synthetic_query: str

class QueryWithFilter(BaseModel):
    database_schema: dict
    gold_collection: str
    gold_filter: IntPropertyFilter | TextPropertyFilter | BooleanPropertyFilter
    synthetic_query: str

# Aggregation Models
class IntAggregation(BaseModel):
    property_name: str
    metrics: Literal["COUNT", "TYPE", "MIN", "MAX", "MEAN", "MEDIAN", "MODE", "SUM"]

class TextAggregation(BaseModel):
    property_name: str
    metrics: Literal["COUNT", "TYPE", "TOP_OCCURRENCES"]
    top_occurrences_limit: Optional[int] = None

class BooleanAggregation(BaseModel):
    property_name: str
    metrics: Literal["COUNT", "TYPE", "TOTAL_TRUE", "TOTAL_FALSE", "PERCENTAGE_TRUE", "PERCENTAGE_FALSE"]

class DateAggregation(BaseModel):
    property_name: str
    metrics: Literal["COUNT", "TYPE", "MIN", "MAX", "MEAN", "MEDIAN", "MODE"]

class QueryWithAggregation(BaseModel):
    database_schema: dict
    gold_collection: str
    gold_aggregation: IntAggregation | TextAggregation| BooleanAggregation
    synthetic_query: str

# Group By Models
class GroupBy(BaseModel):
    property_name: str

class AggregateQuery(BaseModel):
    aggregations: List[IntAggregation | TextAggregation | BooleanAggregation | DateAggregation]
    group_by: Optional[GroupBy] = None
    corresponding_natural_language_query: str

# Aggregation With Query Models
class IntAggregationWithQuery(BaseModel):
    property_name: str
    metrics: Literal["COUNT", "TYPE", "MIN", "MAX", "MEAN", "MEDIAN", "MODE", "SUM"]
    corresponding_natural_language_query: str

class TextAggregationWithQuery(BaseModel):
    property_name: str
    metrics: Literal["COUNT", "TYPE", "TOP_OCCURRENCES"]
    top_occurrences_limit: Optional[int] = None
    corresponding_natural_language_query: str

class BooleanAggregationWithQuery(BaseModel):
    property_name: str
    metrics: Literal["COUNT", "TYPE", "TOTAL_TRUE", "TOTAL_FALSE", "PERCENTAGE_TRUE", "PERCENTAGE_FALSE"]
    corresponding_natural_language_query: str

class SyntheticAggregationQueries(BaseModel):
    int_aggregation_query: IntAggregationWithQuery
    text_aggregation_query: TextAggregationWithQuery
    boolean_aggregation_query: BooleanAggregationWithQuery

# Synthetic Query Models
class SyntheticQuery(BaseModel):
    query: str

class SyntheticSingleAPIQuery(BaseModel):
    query: str
    explanation: str
    api_reference: str

# Filter Operator Types
IntFilterOperator = Literal["=", "<", ">", "<=", ">="]
TextFilterOperator = Literal["=", "LIKE"]
BooleanFilterOperator = Literal["=", "!="]

# Property Filter With Query Models
class IntProperyFilterWithQuery(BaseModel):
    property_name: str
    operator: IntFilterOperator
    value: int | float
    corresponding_natural_language_query: str

class TextPropertyFilterWithQuery(BaseModel):
    property_name: str
    operator: TextFilterOperator
    value: str
    corresponding_natural_language_query: str

class BooleanPropertyFilterWithQuery(BaseModel):
    property_name: str
    operator: BooleanFilterOperator
    value: bool
    corresponding_natural_language_query: str

class SyntheticFilterQueries(BaseModel):
    int_property_filter_query: IntProperyFilterWithQuery
    text_property_filter_query: TextPropertyFilterWithQuery
    boolean_property_filter_query: BooleanPropertyFilterWithQuery

class WeaviateQuery(BaseModel):
    corresponding_natural_language_query: str
    target_collection: str
    search_query: Optional[str]
    integer_property_filter: Optional[IntPropertyFilter]
    text_property_filter: Optional[TextPropertyFilter]
    boolean_property_filter: Optional[BooleanPropertyFilter]
    integer_property_aggregation: Optional[IntAggregation]
    text_property_aggregation: Optional[TextAggregation]
    boolean_property_aggregation: Optional[BooleanAggregation]
    groupby_property: Optional[str]

# Schema Models
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

class WeaviateQueryWithSchema(BaseModel):
    database_schema: WeaviateCollections
    corresponding_natural_language_query: str
    target_collection: str
    search_query: Optional[str]
    integer_property_filter: Optional[IntPropertyFilter]
    text_property_filter: Optional[TextPropertyFilter]
    boolean_property_filter: Optional[BooleanPropertyFilter]
    integer_property_aggregation: Optional[IntAggregation]
    text_property_aggregation: Optional[TextAggregation]
    boolean_property_aggregation: Optional[BooleanAggregation]
    groupby_property: Optional[str]

# Could imagine a more esoteric use case vs. explicit query to this
# This `explanation_...` is a bad idea, better to just create dynamic models
class ToDoWeaviateQuery(BaseModel):
    corresponding_natural_language_query: str
    explanation_of_why_this_query_needs_all_apis_used: str
    target_collection: str
    search_query: Optional[str]
    integer_property_filter: Optional[IntPropertyFilter]
    text_property_filter: Optional[TextPropertyFilter]
    boolean_property_filter: Optional[BooleanPropertyFilter]
    integer_property_aggregation: Optional[IntAggregation]
    text_property_aggregation: Optional[TextAggregation]
    boolean_property_aggregation: Optional[BooleanAggregation]
    groupby_property: Optional[str]


# Pretty sure these two `SimpleSyntheticSchema` / `ComplexSyntheticSchema` aren't used
# ... but I like the idea of controlling the schema complexity
class SimpleSyntheticSchema(BaseModel):
    envisioned_use_case_description: str
    name: str
    text_valued_property_name: str
    int_valued_property_name: str
    boolean_valued_property_name: str

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

# Experimental Models
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

# Function Calling Models
class ParameterProperty(BaseModel):
    type: str
    description: str
    enum: Optional[List[str]] = None

class Parameters(BaseModel):
    type: Literal["object"]
    properties: Dict[str, ParameterProperty]
    required: Optional[List[str]]

class Function(BaseModel):
    name: str
    description: str
    parameters: Parameters

class Tool(BaseModel):
    type: Literal["function"]
    function: Function

# Helper Models
class TestLMConnectionModel(BaseModel):
    generic_response: str

# Execution Models
class QueryPredictionResult(BaseModel):
    query_index: int
    database_schema_index: int
    natural_language_query: str
    ground_truth_query: WeaviateQueryWithSchema
    predicted_query: Optional[WeaviateQuery]
    ast_score: float
    error: Optional[str]

# TODO: Move to src/models/experiment.py
class ExperimentSummary(BaseModel):
    timestamp: str
    model_name: str
    generate_with_models: bool
    total_queries: int
    successful_predictions: int
    failed_predictions: int
    average_ast_score: float
    per_schema_scores: Dict[int, float]
    detailed_results: List[QueryPredictionResult]

# Models for ablation study on Function Calling versus the `ResponseOrToolCalls` Structured Output model
class ToolArguments(BaseModel):
    collection_name: str
    search_query: Optional[str] = None
    integer_property_filter: Optional[IntPropertyFilter] = None
    text_property_filter: Optional[TextPropertyFilter] = None
    boolean_property_filter: Optional[BooleanPropertyFilter] = None
    integer_property_aggregation: Optional[IntAggregation] = None
    text_property_aggregation: Optional[TextAggregation] = None
    boolean_property_aggregation: Optional[BooleanAggregation] = None
    groupby_property: Optional[str] = None

class ToolCall(BaseModel):
    function_name: str
    arguments: ToolArguments

class ResponseOrToolCalls(BaseModel):
    reflection_about_tool_use: Optional[str] = Field(
        default=None,
        description="A rationale regarding whether tool calls are needed."
    )
    use_tools: bool
    response: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None