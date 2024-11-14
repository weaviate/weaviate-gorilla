# Experimental Results

# !! MAYBE NEEDS TO BE UPDATED !!

# AST Test Schema

```python
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

class QueryPredictionResult(BaseModel):
    query_index: int
    database_schema_index: int
    natural_language_query: str
    ground_truth_query: WeaviateQuery
    predicted_query: Optional[WeaviateQuery]
    ast_score: float
    error: Optional[str]

class ExperimentSummary(BaseModel):
    timestamp: str
    model_name: str
    total_queries: int
    successful_predictions: int
    failed_predictions: int
    average_ast_score: float
    per_schema_scores: Dict[int, float]
    detailed_results: List[QueryPredictionResult]
```

![Weaviate Gorilla](../visuals/weaviate-gorillas/gorilla-96.png)
