# Experimental Results

# AST Test Schema

```python
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
