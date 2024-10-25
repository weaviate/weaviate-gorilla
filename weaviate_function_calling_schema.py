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

# We have 4 Weaviate APIs:
'''
All returns a string-valued response

`get_search_results_with_optional_filters(collection_name: str, search_query: str, filter_string: str | None = None)`

`get_objects_with_filters(collection_name: str, filter_string: str)`

`aggregate_property(collection_name: str, property_name: str, aggregation_ops: str)`

`count_objects(collection_name: str, groupby_property_key: str)`
'''

filter_string_syntax_description = """
The filter string syntax allows you to create complex filters for querying Weaviate collections. Here's how to use it:

1. Basic condition: property:operator:value
   - Example: name:==:John
   - Supported operators: ==, !=, >, <, >=, <=, LIKE, CONTAINS_ANY, CONTAINS_ALL, WITHIN

2. Multiple conditions can be combined using AND or OR:
   - Example: age:>:30 AND occupation:==:Engineer

3. Use parentheses for grouping:
   - Example: (age:>:30 AND occupation:==:Engineer) OR (age:<:25 AND student:==:true)

4. Special operators:
   - LIKE: For partial string matching (e.g., name:LIKE:Jo*)
   - CONTAINS_ANY/CONTAINS_ALL: For array properties, values separated by commas
     Example: skills:CONTAINS_ANY:Python,JavaScript
   - WITHIN: For geo-location queries, format is latitude,longitude,distance
     Example: location:WITHIN:52.366667,4.9,10

5. Nested conditions are supported to any depth:
   - Example: (age:>:30 AND (occupation:==:Engineer OR occupation:==:Developer)) OR (age:<:25 AND student:==:true)

Remember to properly encode special characters if passing this string via URL parameters.
"""

weaviate_function_calling_schema = [
    Tool(
        type="function",
        function=Function(
            name="get_search_results_with_optional_filters",
            description="Get search results for a provided query with optional filters.",
            parameters=Parameters(
                type="object",
                properties={
                    "collection_name": ParameterProperty(
                        type="string",
                        description="The name of the collection to search in.",
                    ),
                    "search_query": ParameterProperty(
                        type="string",
                        description="The search query.",
                    ),
                    "filter_string": ParameterProperty(
                        type="string",
                        description=filter_string_syntax_description
                    ),
                },
                required=["collection_name", "search_query"],
            ),
        ),
    ),
    Tool(
        type="function",
        function=Function(
            name="get_objects_with_filters",
            description="Get objects from a collection using filters.",
            parameters=Parameters(
                type="object",
                properties={
                    "collection_name": ParameterProperty(
                        type="string",
                        description="The name of the collection to get objects from.",
                    ),
                    "filter_string": ParameterProperty(
                        type="string",
                        description="The filter string to apply when retrieving objects.",
                    ),
                },
                required=["collection_name", "filter_string"],
            ),
        ),
    ),
    Tool(
        type="function",
        function=Function(
            name="aggregate_property",
            description="Aggregate a property across objects in a collection.",
            parameters=Parameters(
                type="object",
                properties={
                    "collection_name": ParameterProperty(
                        type="string",
                        description="The name of the collection to aggregate from.",
                    ),
                    "property_name": ParameterProperty(
                        type="string",
                        description="The name of the property to aggregate.",
                    ),
                    "aggregation_ops": ParameterProperty(
                        type="string",
                        description="List of aggregation operations to perform.",
                    ),
                },
                required=["collection_name", "property_name", "aggregation_ops"],
            ),
        ),
    ),
    Tool(
        type="function",
        function=Function(
            name="count_objects",
            description="Count objects in a collection, optionally grouped by a property.",
            parameters=Parameters(
                type="object",
                properties={
                    "collection_name": ParameterProperty(
                        type="string",
                        description="The name of the collection to count objects in.",
                    ),
                    "groupby_property_key": ParameterProperty(
                        type="string",
                        description="The property key to group the count by.",
                    ),
                },
                required=["collection_name"],
            ),
        ),
    ),
]