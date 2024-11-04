# Filter Domain-Specific Language (string type)

### Concept (Not Tested)

```python
from typing import List, Dict, Optional, Literal, Union
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
    type: "function"
    function: Function

tools = [Tool(
        type="function",
        function=Function(
            name="query_database",
            description=f"""Query a database.

            Available collections in this database:
            {collections_description}""",
            parameters=Parameters(
                type="object",
                properties={
                    "collection_name": ParameterProperty(
                        type="string",
                        description="The collection to query",
                        enum=collections_list
                    ),
                    "search_query": ParameterProperty(
                        type="string",
                        description="Optional search query to find semantically relevant items."
                    ),
                    "filter_string": ParameterProperty(
                        type="string",
                        description="""
                        Optional filter expression using prefix notation to ensure unambiguous order of operations.
                        
                        Basic condition syntax: property_name:operator:value
                        
                        Compound expressions use prefix AND/OR with parentheses:
                        - AND(condition1, condition2)
                        - OR(condition1, condition2)
                        - AND(condition1, OR(condition2, condition3))
                        
                        Examples:
                        - Simple: age:>:25
                        - Compound: AND(age:>:25, price:<:1000)
                        - Complex: OR(AND(age:>:25, price:<:1000), category:=:'electronics')
                        - Nested: AND(status:=:'active', OR(price:<:50, AND(rating:>:4, stock:>:100)))
                        
                        Supported operators:
                        - Comparison: =, >, <, >=, <= 
                        - Text only: LIKE

                        IMPORTANT!!! Please review the collection schema to make sure the property name is spelled correctly!! THIS IS VERY IMPORTANT!!!
                        """
                    )
                },
                required=["collection_name"]
            )
        )
)]
```
