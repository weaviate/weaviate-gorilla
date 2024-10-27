# Function Calling with Weaviate

Today, most agents in production add a fairly simple semantic search to their schema as follows:
```python
def search_database_collection(
    weaviate_client: weaviate.WeaviateClient,
    collection_name: str,
    search_query: str,
    alpha: float,
    limit: int
    ) -> str:
    search_collection = weaviate_client.collections.get(collection_name)
    results = search_collection.query.hybrid_search(
        query=search_query,
        alpha=alpha,
        limit=limit
    )
    return results
```



This is then interfaced in a function calling JSON schema with the following:

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


get_objects_tool = Tool(
    type="function",
    function=Function(
        name="get_objects_{collection_name}",
        description="Get objects from a database collection named {collection_name} that match specific filter criteria.",
        parameters=Parameters(
            type="object",
            properties={
                "where_filter": ParameterProperty(
                    type="object",
                    description="Filter conditions to match objects against (e.g. {\"path\": [\"property\"], \"operator\": \"Equal\", \"valueText\": \"value\"})"
                ),
                "limit": ParameterProperty(
                    type="integer",
                    description="Maximum number of objects to return",
                    default=10
                )
            },
            required=["where_filter"]
        )
    )
)
```