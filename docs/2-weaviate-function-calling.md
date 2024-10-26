# Function Calling with Weaviate

Today, most agents in production add a fairly simple semantic search to their schema as follows:
```python
def search_blogs(
    weaviate_client: weaviate.WeaviateClient,
    collection_name: str,
    search_query: str
    ) -> str:
    search_collection = weaviate_client.collections.get(collection_name)
    results = search_collection.query.hybrid_search()
    return results
```

This is then interfaced in a function calling JSON schema with the following:

```python
from weaviate.function_calling import Tool

search_tool = Tool(
    type="function",
    function=Function(
        name="search_blogs",
        description="Search for blog posts using a semantic search query",
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

This is the standard tool schema that LLM APIs such as OpenAI, Anthropic, Gemini, Ollama, and vLLM use, to name a few.