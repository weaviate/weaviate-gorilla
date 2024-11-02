# Concept (Not Tested)

```python
from typing import List, Dict, Optional, Literal, Union
from pydantic import BaseModel, Field
from enum import Enum

class FilterOperator(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

class ComparisonOperator(str, Enum):
    EQUALS = "="
    GREATER = ">"
    LESS = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "CONTAINS"
    LIKE = "LIKE"

class FilterCondition(BaseModel):
    property: str
    operator: ComparisonOperator
    value: Union[str, int, float, bool]

class FilterExpression(BaseModel):
    operator: FilterOperator
    conditions: List[Union['FilterExpression', FilterCondition]]

class SearchParameters(BaseModel):
    collection_name: str
    search_query: Optional[str] = None
    filter: Optional[Union[FilterCondition, FilterExpression]] = None
    raw_filter: Optional[str] = None  # Fallback for complex cases

class Tool(BaseModel):
    type: Literal["function"]
    function: Function

def create_weaviate_search_tool(collections_description: str, collections_list: List[str]) -> Tool:
    return Tool(
        type="function",
        function=Function(
            name="search_weaviate_collection",
            description="Search through a Weaviate Collection with hybrid filtering options.",
            parameters=Parameters(
                type="object",
                properties={
                    "collection_name": ParameterProperty(
                        type="string",
                        description=f"The Weaviate Collection to search. Available collections: {collections_description}",
                        enum=collections_list
                    ),
                    "search_query": ParameterProperty(
                        type="string",
                        description="The semantic search query to find relevant items."
                    ),
                    "structured_filter": ParameterProperty(
                        type="string",
                        description="""
                        A structured filter in JSON format. Examples:
                        
                        Simple condition:
                        {
                            "property": "age",
                            "operator": ">",
                            "value": 25
                        }
                        
                        Compound condition:
                        {
                            "operator": "AND",
                            "conditions": [
                                {
                                    "property": "age",
                                    "operator": ">",
                                    "value": 25
                                },
                                {
                                    "operator": "OR",
                                    "conditions": [
                                        {
                                            "property": "category",
                                            "operator": "=",
                                            "value": "electronics"
                                        },
                                        {
                                            "property": "price",
                                            "operator": "<",
                                            "value": 100
                                        }
                                    ]
                                }
                            ]
                        }
                        """
                    ),
                    "raw_filter": ParameterProperty(
                        type="string",
                        description="""
                        For advanced users: A raw filter string using the flexible syntax.
                        Warning: Use this only when the structured filter cannot express your needs.
                        
                        Example: AND(age:>:25, OR(category:=:'electronics', price:<:100))
                        """
                    )
                },
                required=["collection_name"]
            )
        )
    )

def parse_raw_filter(raw_filter: str) -> Union[FilterCondition, FilterExpression]:
    """Convert raw filter string to structured format"""
    # Implementation would go here
    pass

def execute_search(params: SearchParameters):
    """Execute the search with either structured or raw filter"""
    if params.raw_filter:
        try:
            structured_filter = parse_raw_filter(params.raw_filter)
            return execute_structured_search(params.collection_name, params.search_query, structured_filter)
        except Exception as e:
            # Log the error and fall back to direct execution
            return execute_raw_search(params.collection_name, params.search_query, params.raw_filter)
    else:
        return execute_structured_search(params.collection_name, params.search_query, params.filter)
```