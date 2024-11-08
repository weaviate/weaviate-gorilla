# Models used

```python
class SyntheticAggregationQueries(BaseModel):
    int_aggregation_query: IntAggregationWithQuery
    text_aggregation_query: TextAggregationWithQuery
    boolean_aggregation_query: BooleanAggregationWithQuery

class SyntheticFilterQueries(BaseModel):
    int_property_filter_query: IntProperyFilterWithQuery
    text_property_filter_query: TextPropertyFilterWithQuery
    boolean_property_filter_query: BooleanPropertyFilterWithQuery

# Collection Routing Queries is using 2 models for generation and saving
class SyntheticQuery(BaseModel):
    query: str

class CollectionRouterQuery(BaseModel):
    database_schema: dict
    gold_collection: str 
    synthetic_query: str
```

## Helpers for `SyntheticFilterQueries`

```python
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
```

## Helpers for `SyntheticAggregateQueries`

```python
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
```