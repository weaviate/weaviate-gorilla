# Data Schemas

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

![Weaviate Gorilla](../visuals/weaviate-gorillas/gorilla-63.png)