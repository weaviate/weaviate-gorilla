from pydantic import BaseModel
from typing import Literal, Dict, List, Optional

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
    
def build_weaviate_query_tool(collections_description: str, collections_list: list[str]) -> Tool:
    return Tool(
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
                ),
                "aggregate_string": ParameterProperty(
                    type="string",
                    description="""
                    Optional aggregate expression

                    Basic property aggregation syntax: property_name:aggregation_type

                    Group by syntax: GROUP_BY(property_name)
                    - Note: Currently limited to one property or cross-reference. Nested paths are not supported.

                    Available Aggregation Types
                    Based on data type:

                    Text Properties
                    - COUNT
                    - TYPE
                    - TOP_OCCURRENCES[limit] - Optional limit parameter for minimum count

                    Numeric Properties (Number/Integer)
                    - COUNT
                    - TYPE
                    - MIN
                    - MAX
                    - MEAN
                    - MEDIAN
                    - MODE
                    - SUM

                    Boolean Properties
                    - COUNT
                    - TYPE
                    - TOTAL_TRUE
                    - TOTAL_FALSE
                    - PERCENTAGE_TRUE
                    - PERCENTAGE_FALSE

                    Date Properties
                    - COUNT
                    - TYPE
                    - MIN
                    - MAX
                    - MEAN
                    - MEDIAN
                    - MODE

                    Examples

                    Simple Aggregations

                    # Count all records in the collection
                    Article:COUNT

                    # Get wordCount (TEXT property) statistics
                    wordCount:COUNT,wordCount:MEAN,wordCount:MAX

                    # Get top occurrences of categories (TEXT property) with minimum count of 5
                    category:TOP_OCCURRENCES[5]

                    Grouped Aggregations

                    # Group by publication and get counts
                    GROUP_BY(publication):COUNT

                    # Group by category with multiple metrics
                    GROUP_BY(category):COUNT,price:MEAN,price:MAX

                    ## Combining Multiple Aggregations
                    Multiple aggregations can be combined using comma separation:

                    GROUP_BY(publication):COUNT,wordCount:MEAN,category:TOP_OCCURRENCES[5]
                    """
                )
            },
            required=["collection_name"]
        )
    )
)]