# 2. Function Calling with Weaviate

## Tool Schemas

In order to prompt the agent with the tools it has access to, the AI industry has settled on the `function calling` schema.

Here is a Pydantic Model defining this:

```python
class ParameterProperty(BaseModel):
    type: str
    description: str

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
```

This is the standard tool schema that LLM APIs such as OpenAI, Anthropic, Gemini, Ollama, and vLLM use, to name a few.

## Weaviate as a `Tool` Instance

# Note, this needs to be updated

```python
from weaviate.function_calling import Tool

search_tool = Tool(
    type="function",
    function=Function(
        name="search_{collection_name}",
        description="Search for items in a database collection named {collection_name} determined to be most relevant to the search query.",
        parameters=Parameters(
            type="object",
            properties={
                "search_query": ParameterProperty(
                    type="string",
                    description="The search query to find relevant blog posts"
                )
            },
            required=["search_query"]
        )
    )
)
```

# Query Database

```
def query_database(
    weaviate_client: weaviate.WeaviateClient,
    collection_name: str,
    search_query: Optional[str] = None,
    filter_string: Optional[str] = None,
    aggregation_string: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query a Weaviate database with optional search, filter, and aggregation parameters.
    
    Args:
        weaviate_client: The Weaviate client instance
        collection_name: Name of the collection to query
        search_query: Optional search query string for hybrid search
        filter_string: Optional filter string in format "property:operator:value" with AND/OR
        aggregation_string: Optional aggregation string in format "GROUP_BY(prop) METRICS(prop:type[metrics])"
    
    Returns:
        Dict containing query results with keys based on the query type:
        - 'objects': List of objects if search/filter was used
        - 'aggregations': Aggregation results if aggregation was used
    """
    collection = weaviate_client.collections.get(collection_name)
    
    # Parse filter if provided
    filter_obj = None
    if filter_string:
        filter_obj = _build_weaviate_filter(filter_string)
    
    # Parse aggregation if provided
    group_by, metrics = None, None
    if aggregation_string:
        group_by, metrics = _build_weaviate_aggregation(aggregation_string)
    
    result: Dict[str, Any] = {}
    
    # Case 1: Only aggregation
    if aggregation_string and not (search_query or filter_string):
        agg_response = collection.aggregate.over_all(
            group_by=group_by,
            return_metrics=metrics
        )
        result['aggregations'] = {
            'total_count': agg_response.total_count,
            'groups': [{
                'group': g.grouped_by,
                'properties': g.properties
            } for g in agg_response.groups] if agg_response.groups else None
        }
    
    # Case 2: Search with optional filter and/or aggregation
    elif search_query:
        hybrid_response = collection.query.hybrid(
            query=search_query,
            filters=filter_obj,
            return_metadata=MetadataQuery(score=True),
            limit=10  # Configurable
        )
        
        if aggregation_string:
            agg_response = collection.aggregate.over_all(
                group_by=group_by,
                return_metrics=metrics,
                filters=filter_obj  # Apply same filters to aggregation
            )
            result['aggregations'] = {
                'total_count': agg_response.total_count,
                'groups': [{
                    'group': g.grouped_by,
                    'properties': g.properties
                } for g in agg_response.groups] if agg_response.groups else None
            }
        
        result['objects'] = [{
            'properties': obj.properties,
            'score': obj.metadata.score
        } for obj in hybrid_response.objects]
    
    # Case 3: Only filter
    elif filter_string:
        filter_response = collection.query.fetch_objects(
            filters=filter_obj,
            limit=10  # Configurable
        )
        
        if aggregation_string:
            agg_response = collection.aggregate.over_all(
                group_by=group_by,
                return_metrics=metrics,
                filters=filter_obj
            )
            result['aggregations'] = {
                'total_count': agg_response.total_count,
                'groups': [{
                    'group': g.grouped_by,
                    'properties': g.properties
                } for g in agg_response.groups] if agg_response.groups else None
            }
        
        result['objects'] = [{
            'properties': obj.properties
        } for obj in filter_response.objects]
    
    return result
```