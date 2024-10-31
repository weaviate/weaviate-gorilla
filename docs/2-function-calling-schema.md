# Function Calling with Weaviate

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
