# 3. Weaviate as a Function

### Quick References for Weaviate Functions

## Search Hard-Coded Collection

```python
def code_search(query: str) -> str:
    """Sends a query to Weaviate's Hybrid Search. Parases the response into a {k}:{v} string."""
    
    response = code_collection.query.hybrid(query, limit=5)
    
    stringified_response = ""
    for idx, o in enumerate(response.objects):
        stringified_response += f"Search Result: {idx+1}:\n"
        for prop in o.properties:
            stringified_response += f"{prop}:{o.properties[prop]}"
        stringified_response += "\n"
    
    return stringified_response
```

## (More General) Collection Name as a Search Argument

```python
def get_collections_info(client: weaviate.WeaviateClient) -> tuple[str, list[str]]:
    """
    Get detailed information about all collections in a Weaviate instance.
    
    Args:
        client: A Weaviate client instance
    
    Returns:
        tuple[str, list[str]]: Tuple containing formatted collection details string and list of collection names
    """
    
    collections = client.collections.list_all()
    
    # Get collection names as list
    collection_names = list(collections.keys())
    
    # Build output string
    output = []
    for collection_name, config in collections.items():
        output.append(f"\nCollection Name: {collection_name}")
        output.append(f"Description: {config.description}")
        output.append("\nProperties:")
        for prop in config.properties:
            output.append(f"- {prop.name}: {prop.description} (type: {prop.data_type.value})")
    
    return "\n".join(output), collection_names

# Call the function with our client and print result
info_str, collections_list = get_collections_info(weaviate_client)
print(info_str)
```

# Connect to Tool

```python
from typing import Literal, Optional, Dict, List, Union
from pydantic import BaseModel

class ParameterProperty(BaseModel):
    type: str
    description: str
    enum: Optional[List[str]] = None

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

# Example usage:
search_tool = Tool(
    type="function",
    function=Function(
        name="search_weaviate_collection",
        description="Search for the most relevant items to the provided `search_query` in a Weaviate Database Collection.",
        parameters=Parameters(
            type="object",
            properties={
                "collection_name": ParameterProperty(
                    type="string",
                    description="The Weaviate Collection to search through.",
                    enum=collections_list
                ),
                "search_query": ParameterProperty(
                    type="string",
                    description="The search query."
                )
            },
            required=["collection_name", "search_query"]
        )
    )
)

# Example of another tool:
calculate_avg_tool = Tool(
    type="function", 
    function=Function(
        name="calculate_average",
        description="Calculate the average of a numeric property across collection items",
        parameters=Parameters(
            type="object",
            properties={
                "collection_name": ParameterProperty(
                    type="string",
                    description="The Weaviate Collection to analyze",
                    enum=collections_list
                ),
                "property_name": ParameterProperty(
                    type="string",
                    description="The numeric property to average"
                )
            },
            required=["collection_name", "property_name"]
        )
    )
)
```

### Discussion
- Client-Server Authentication
- Load Balancers for Agents
- Task Queues for Agentic Planning