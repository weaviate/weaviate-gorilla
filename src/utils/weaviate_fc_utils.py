import weaviate
from weaviate.classes.query import Filter

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

def _build_weaviate_filter(filter_string: str) -> Filter:
    def _parse_condition(condition: str) -> Filter:
        parts = condition.split(':')
        if len(parts) < 3:
            raise ValueError(f"Invalid condition: {condition}")
        
        property, operator, value = parts[0], parts[1], ':'.join(parts[2:])
        
        if operator == '==':
            return Filter.by_property(property).equal(value)
        elif operator == '!=':
            return Filter.by_property(property).not_equal(value)
        elif operator == '>':
            return Filter.by_property(property).greater_than(float(value))
        elif operator == '<':
            return Filter.by_property(property).less_than(float(value))
        elif operator == '>=':
            return Filter.by_property(property).greater_than_equal(float(value))
        elif operator == '<=':
            return Filter.by_property(property).less_than_equal(float(value))
        elif operator == 'LIKE':
            return Filter.by_property(property).like(value)
        elif operator == 'CONTAINS_ANY':
            return Filter.by_property(property).contains_any(value.split(','))
        elif operator == 'CONTAINS_ALL':
            return Filter.by_property(property).contains_all(value.split(','))
        elif operator == 'WITHIN':
            lat, lon, dist = map(float, value.split(','))
            return Filter.by_property(property).within_geo_range(lat, lon, dist)
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def _parse_group(group: str) -> Filter:
        if 'AND' in group:
            conditions = [_parse_group(g.strip()) for g in group.split('AND')]
            return Filter.all_of(conditions)
        elif 'OR' in group:
            conditions = [_parse_group(g.strip()) for g in group.split('OR')]
            return Filter.any_of(conditions)
        else:
            return _parse_condition(group)

    # Remove outer parentheses if present
    filter_string = filter_string.strip()
    if filter_string.startswith('(') and filter_string.endswith(')'):
        filter_string = filter_string[1:-1]

    return _parse_group(filter_string)

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
)