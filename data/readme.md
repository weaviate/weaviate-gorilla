# Data Schemas

## WeaviateQuery

```python
class WeaviateQuery(BaseModel):
    target_collection: str
    search_query: Optional[str]
    integer_property_filter: Optional[IntPropertyFilter]
    text_property_filter: Optional[TextPropertyFilter]
    boolean_property_filter: Optional[BooleanPropertyFilter]
    integer_property_aggregation: Optional[IntAggregation]
    text_property_aggregation: Optional[TextAggregation]
    boolean_property_aggregation: Optional[BooleanAggregation]
    groupby_property: Optional[str]
    corresponding_natural_language_query: str
```

## `collection-routing-queries.json`

Created with `generate_collection_routing_queries.py`

```python
class CollectionRouterQuery(BaseModel):
    database_schema: dict
    gold_collection: str 
    synthetic_query: str
```

## `simple-3-collection-schemas.json`

Created with `generate_schemas.py`

Post-processed with `clean_up_schemas.py`

```python
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
```

![Weaviate Gorilla](../visuals/weaviate-gorillas/gorilla-103.png)
