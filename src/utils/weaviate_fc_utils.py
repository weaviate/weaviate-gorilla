import weaviate
from weaviate.classes.query import Filter, Metrics
from weaviate.classes.aggregate import GroupByAggregate
from src.models import (
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation,
    GroupBy
)
import re
from typing import Tuple, Union, Any

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
        # output.append(f"Description: {config.description}") # 1024 token limit on tool description
        output.append("\nProperties:")
        for prop in config.properties:
            output.append(f"- {prop.name}: {prop.description} (type: {prop.data_type.value})")
    
    return "\n".join(output), collection_names

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
    
# This is going to have to either return `OpenAITool | OllamaTool | AnthropicTool`
# or I can add a type cast type of thing on top of the OpenAITool
def build_weaviate_query_tools(collections_description: str, collections_list: list[str], num_tools: int = 5) -> list[Tool]:
    from src.utils.tool_descriptions import (
        collection_name_descriptions,
        search_query_descriptions, 
        filter_string_descriptions,
        aggregation_string_descriptions
    )

    tools = []
    for i in range(num_tools):
        tools.append(Tool(
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
                            description=collection_name_descriptions[i],
                            enum=collections_list
                        ),
                        "search_query": ParameterProperty(
                            type="string",
                            description=search_query_descriptions[i]
                        ),
                        "filter_string": ParameterProperty(
                            type="string",
                            description=filter_string_descriptions[i]
                        ),
                        "aggregate_string": ParameterProperty(
                            type="string",
                            description=aggregation_string_descriptions[i]
                        )
                    },
                    required=["collection_name"]
                )
            )
        ))
    return tools

def build_weaviate_query_tool(collections_description: str, collections_list: list[str]) -> Tool:
    from src.utils.tool_descriptions import (
        collection_name_descriptions,
        search_query_descriptions,
        filter_string_descriptions,
        aggregation_string_descriptions
    )

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
                        description=collection_name_descriptions[0],
                        enum=collections_list
                    ),
                    "search_query": ParameterProperty(
                        type="string",
                        description=search_query_descriptions[0]
                    ),
                    "filter_string": ParameterProperty(
                        type="string",
                        description=filter_string_descriptions[0]
                    ),
                    "aggregate_string": ParameterProperty(
                        type="string",
                        description=aggregation_string_descriptions[0]
                    )
                },
                required=["collection_name"]
            )
        )
    )

# Anthropic Tool
class AnthropicToolInputSchema(BaseModel):
    type: str
    properties: dict[str, Any]
    required: list[str]

class AnthropicTool(BaseModel):
    name: str
    description: str
    input_schema: AnthropicToolInputSchema

# Abstract this to one function that takes the model_provider as an argument
def build_weaviate_query_tool_for_anthropic(collections_description: str, collections_list: list[str]) -> AnthropicTool:
    return AnthropicTool(
        name="query_database",
        description=f"""Query a database.

        Available collections in this database:
        {collections_description}""",
        input_schema=AnthropicToolInputSchema(
            type="object",
            properties={
                "collection_name": {
                    "type": "string",
                    "description": "The collection to query",
                    "enum": collections_list
                },
                "search_query": {
                    "type": "string",
                    "description": "Optional search query to find semantically relevant items."
                },
                "filter_string": {
                    "type": "string", 
                    "description": """
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
                },
                "aggregate_string": {
                    "type": "string",
                    "description": """
                    Optional aggregate expression using syntax: property_name:aggregation_type.

                    Group by with: GROUP_BY(property_name) (limited to one property).

                    Aggregation Types by Data Type:

                    Text: COUNT, TYPE, TOP_OCCURRENCES[limit]
                    Numeric: COUNT, TYPE, MIN, MAX, MEAN, MEDIAN, MODE, SUM
                    Boolean: COUNT, TYPE, TOTAL_TRUE, TOTAL_FALSE, PERCENTAGE_TRUE, PERCENTAGE_FALSE
                    Date: COUNT, TYPE, MIN, MAX, MEAN, MEDIAN, MODE

                    Examples:

                    Simple: Article:COUNT, wordCount:COUNT,MEAN,MAX, category:TOP_OCCURRENCES[5]
                    Grouped: GROUP_BY(publication):COUNT, GROUP_BY(category):COUNT,price:MEAN,MAX

                    Combine with commas: GROUP_BY(publication):COUNT,wordCount:MEAN,category:TOP_OCCURRENCES[5]
                    """
                }
            },
            required=["collection_name"]
        )
    )

class OllamaFunctionParameters(BaseModel):
    type: Literal["object"] = "object"
    properties: dict[str, dict[str, Any]]
    required: list[str]

class OllamaFunction(BaseModel):
    name: str
    description: str
    parameters: OllamaFunctionParameters

class OllamaTool(BaseModel):
    type: Literal["function"] = "function"
    function: OllamaFunction

def build_weaviate_query_tool_for_ollama(collections_description: str, collections_list: list[str]) -> OllamaTool:
    query_parameters = {
        "type": "object",
        "properties": {
            "target_collection": {
                "type": "string",
                "description": "The collection to retrieve objects from."
            },
            "search_query": {
                "type": "string",
                "description": "A search query to return objects from a search index."                
            },
            "integer_property_filter": {
                "type": "object",
                "description": "Filter numeric properties using comparison operators",
                "properties": {
                    "property_name": {"type": "string"},
                    "operator": {"type": "string", "enum": ["=", "<", ">", "<=", ">="]},
                    "value": {"type": "number"}
                },
                "required": ["property_name", "operator", "value"]
            },
            "text_property_filter": {
                "type": "object",
                "description": "Filter text properties using equality or LIKE operators",
                "properties": {
                    "property_name": {"type": "string"},
                    "operator": {"type": "string", "enum": ["=", "LIKE"]},
                    "value": {"type": "string"}
                },
                "required": ["property_name", "operator", "value"]
            },
            "boolean_property_filter": {
                "type": "object",
                "description": "Filter boolean properties using equality operators",
                "properties": {
                    "property_name": {"type": "string"},
                    "operator": {"type": "string", "enum": ["=", "!="]},
                    "value": {"type": "boolean"}
                },
                "required": ["property_name", "operator", "value"]
            },
            "integer_property_aggregation": {
                "type": "object",
                "description": "Aggregate numeric properties using statistical functions",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["COUNT", "TYPE", "MIN", "MAX", "MEAN", "MEDIAN", "MODE", "SUM"]}
                },
                "required": ["property_name", "metrics"]
            },
            "text_property_aggregation": {
                "type": "object",
                "description": "Aggregate text properties using frequency analysis",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["COUNT", "TYPE", "TOP_OCCURRENCES"]},
                    "top_occurrences_limit": {"type": "integer"}
                },
                "required": ["property_name", "metrics"]
            },
            "boolean_property_aggregation": {
                "type": "object",
                "description": "Aggregate boolean properties using statistical functions",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["COUNT", "TYPE", "TOTAL_TRUE", "TOTAL_FALSE", "PERCENTAGE_TRUE", "PERCENTAGE_FALSE"]}
                },
                "required": ["property_name", "metrics"]
            },
            "groupby_property": {
                "type": "string",
                "description": "Group the results by a property."
            }
        },
        "required": ["target_collection"]
    }
    query_function = Function(
        name="query_database",
        description="Query a database to retrieve objects.",
        parameters=query_parameters
    )
    return OllamaTool(
        function=query_function
    )


'''
# Leave to ablate DSL / Models later on
def build_weaviate_query_tool_for_ollama(collections_description: str, collections_list: list[str]) -> OllamaTool:
    return OllamaTool(
        type="function",
        function=OllamaFunction(
            name="query_database",
            description=f"""Query a database.

            Available collections in this database:
            {collections_description}""",
            parameters=OllamaFunctionParameters(
                type="object",
                properties={
                    "collection_name": {
                        "type": "string",
                        "description": "The collection to query",
                        "enum": collections_list
                    },
                    "search_query": {
                        "type": "string",
                        "description": "Optional search query to find semantically relevant items."
                    },
                    "filter_string": {
                        "type": "string",
                        "description": """
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
                    },
                    "aggregate_string": {
                        "type": "string",
                        "description": """
                        Optional aggregate expression using syntax: property_name:aggregation_type.

                        Group by with: GROUP_BY(property_name) (limited to one property).

                        Aggregation Types by Data Type:

                        Text: COUNT, TYPE, TOP_OCCURRENCES[limit]
                        Numeric: COUNT, TYPE, MIN, MAX, MEAN, MEDIAN, MODE, SUM
                        Boolean: COUNT, TYPE, TOTAL_TRUE, TOTAL_FALSE, PERCENTAGE_TRUE, PERCENTAGE_FALSE
                        Date: COUNT, TYPE, MIN, MAX, MEAN, MEDIAN, MODE

                        Examples:

                        Simple: Article:COUNT, wordCount:COUNT,MEAN,MAX, category:TOP_OCCURRENCES[5]
                        Grouped: GROUP_BY(publication):COUNT, GROUP_BY(category):COUNT,price:MEAN,MAX

                        Combine with commas: GROUP_BY(publication):COUNT,wordCount:MEAN,category:TOP_OCCURRENCES[5]
                        """
                    }
                },
                required=["collection_name"]
            )
        )
    )
'''


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

def _build_weaviate_filter_return_model(filter_string: str):
    def _parse_condition(condition: str):
        parts = condition.split(':')
        if len(parts) < 3:
            raise ValueError(f"Invalid condition: {condition}")
        
        property, operator, value = parts[0], parts[1], ':'.join(parts[2:])
        
        if operator in ['>', '<', '>=', '<=']:
            return IntPropertyFilter(property_name=property, operator=operator, value=float(value))
        elif operator in ['=', '==']:  # Handle both = and == operators
            if value.lower() in ['true', 'false']:
                return BooleanPropertyFilter(property_name=property, operator=operator, value=value.lower() == 'true')
            try:
                return IntPropertyFilter(property_name=property, operator=operator, value=float(value))
            except ValueError:
                return TextPropertyFilter(property_name=property, operator=operator, value=value)
        elif operator == 'LIKE':
            return TextPropertyFilter(property_name=property, operator=operator, value=value)
        elif operator == '!=':
            if value.lower() in ['true', 'false']:
                return BooleanPropertyFilter(property_name=property, operator=operator, value=value.lower() == 'true')
            try:
                return IntPropertyFilter(property_name=property, operator=operator, value=float(value))
            except ValueError:
                return TextPropertyFilter(property_name=property, operator=operator, value=value)
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def _parse_group(group: str):
        # Handle AND/OR groups with parentheses
        if group.startswith('AND(') or group.startswith('OR('):
            operator = group[:3] if group.startswith('AND') else group[:2]
            content = group[group.find('(')+1:group.rfind(')')]
            conditions = []
            
            # Split by comma while respecting nested parentheses
            current = ''
            paren_count = 0
            for char in content:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == ',' and paren_count == 0:
                    conditions.append(_parse_group(current.strip()))
                    current = ''
                    continue
                current += char
            if current:
                conditions.append(_parse_group(current.strip()))
                
            return conditions
        elif 'AND' in group:
            conditions = [_parse_group(g.strip()) for g in group.split('AND')]
            return conditions
        elif 'OR' in group:
            conditions = [_parse_group(g.strip()) for g in group.split('OR')]
            return conditions
        else:
            return _parse_condition(group)

    return _parse_group(filter_string)

def _build_weaviate_aggregation_return_model(agg_string: str) -> Tuple[Optional[GroupBy], List[Union[IntAggregation, TextAggregation, BooleanAggregation]]]:
    """
    Parses an aggregation string into Weaviate GroupBy and Aggregation models.
    
    Format:
    GROUP_BY(property) METRICS(property:type[metrics], property2:type[metrics])
    
    Examples:
    - "GROUP_BY(publication) METRICS(wordCount:int[count,mean,max])"
    - "METRICS(rating:num[mean,sum], title:text[count,topOccurrences])"
    - "GROUP_BY(author) METRICS(isPublished:bool[totalTrue,percentageFalse])"
    
    Returns:
    Tuple of (GroupBy, List[Aggregation])
    """
    def _parse_metrics(metrics_str: str) -> List[Union[IntAggregation, TextAggregation, BooleanAggregation]]:
        # Extract content within METRICS(...)
        metrics_list = []
        
        # Split multiple metrics definitions by comma, but not within brackets
        metrics_parts = []
        current_part = ""
        bracket_count = 0
        
        for char in metrics_str:
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            elif char == ',' and bracket_count == 0:
                metrics_parts.append(current_part.strip())
                current_part = ""
                continue
            current_part += char
        if current_part:
            metrics_parts.append(current_part.strip())
        
        # Parse each metric definition
        for metric in metrics_parts:
            # Parse property:type[operations]
            match = re.match(r'(\w+):(text|int|num|bool)\[([\w,]+)\]', metric.strip())
            if not match:
                raise ValueError(f"Invalid metrics format: {metric}")
            
            prop_name, data_type, operations = match.groups()
            operations = [op.strip() for op in operations.split(',')]
            
            # Create appropriate Aggregation object based on type
            if data_type == 'text':
                metric_obj = TextAggregation(
                    property_name=prop_name,
                    metrics=operations,
                    top_occurrences_limit=None  # Adjust as needed
                )
            elif data_type in ('int', 'num'):
                metric_obj = IntAggregation(
                    property_name=prop_name,
                    metrics=operations
                )
            elif data_type == 'bool':
                metric_obj = BooleanAggregation(
                    property_name=prop_name,
                    metrics=operations
                )
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
            metrics_list.append(metric_obj)
        
        return metrics_list

    def _parse_group_by(group_str: str) -> GroupBy:
        # Extract property name from GROUP_BY(property)
        match = re.match(r'GROUP_BY\((\w+)\)', group_str)
        if not match:
            raise ValueError(f"Invalid GROUP_BY format: {group_str}")
        
        return GroupBy(property_name=match.group(1))

    # Initialize return values
    group_by = None
    metrics = []
    
    # Split into parts by space, but not within parentheses
    parts = []
    current_part = ""
    paren_count = 0
    
    for char in agg_string:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        elif char.isspace() and paren_count == 0:
            if current_part:
                parts.append(current_part)
            current_part = ""
            continue
        current_part += char
    if current_part:
        parts.append(current_part)
    
    # Parse each part
    for part in parts:
        if part.startswith('GROUP_BY'):
            if group_by is not None:
                raise ValueError("Multiple GROUP_BY clauses not allowed")
            group_by = _parse_group_by(part)
        elif part.startswith('METRICS'):
            # Extract content within METRICS(...)
            match = re.match(r'METRICS\((.*)\)', part)
            if not match:
                raise ValueError(f"Invalid METRICS format: {part}")
            metrics.extend(_parse_metrics(match.group(1)))
    
    return group_by, metrics