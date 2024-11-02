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

# Would you wrap `Union[FilterCondition, FilterExpression] in something else

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
                        type="FilterCondition",
                        description="Return objects that match the filter.
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
```
