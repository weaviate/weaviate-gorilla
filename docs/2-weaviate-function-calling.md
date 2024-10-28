# Function Calling with Weaviate

Today, most agents in production add a fairly simple semantic search to their schema as follows:
```python
def search_weaviate_collection(
    self,
    collection_name: str,
    search_query: str,
):
    """
    This tool queries an external database collection
    named by the parameter {collection_name} to find the most semantically similar items to the query.

    Args: 
        collection_name (str): The name of the database collection
        search_query (str): The search query

    Returns: 
        search_results (str): The results from the search engine.
    """
    import weaviate
    from weaviate.classes.init import Auth
    import os

    weaviate_client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.environ["WEAVIATE_URL"],
        auth_credentials=Auth.api_key(os.environ["WEAVIATE_API_KEY"]),
        headers={
            "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]
        }
    )

    weaviate_collection = weaviate_client.collections.get(collection_name)
    query_result = weaviate_collection.query.hybrid(
        query=search_query,
        alpha=0.5,
        limit=5
    )
    weaviate_client.close()
    results = query_result.objects
    formatted_results = "\n".join(
        [f"[Search Result {i+1}] {str(result.properties)}" for i, result in enumerate(results)]
    )
    return formatted_results
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
