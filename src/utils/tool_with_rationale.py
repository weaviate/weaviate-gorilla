from src.models import (
    OpenAIParameters,
    OpenAIFunction,
    OpenAITool,
    AnthropicTool,
    AnthropicToolInputSchema,
    OllamaFunctionParameters,
    OllamaFunction,
    OllamaTool
)
import re
from typing import Tuple, Union, Any
from pydantic import BaseModel
from typing import Literal, Dict, List, Optional

def build_weaviate_query_tool_for_openai_with_rationale(collections_description: str, collections_list: list[str], generate_with_models: bool = False) -> OpenAITool:
    if generate_with_models:
        properties = {
            "tool_rationale": {
                "type": "string",
                "description": "A rationale explaining why these particular argument values will help assist the user."
            },
            "collection_name": {
                "type": "string",
                "description": "The collection to query.",
                "enum": collections_list
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
                }
            },
            "text_property_filter": {
                "type": "object", 
                "description": "Filter text properties using equality or LIKE operators",
                "properties": {
                    "property_name": {"type": "string"},
                    "operator": {"type": "string", "enum": ["=", "LIKE"]},
                    "value": {"type": "string"}
                }
            },
            "boolean_property_filter": {
                "type": "object",
                "description": "Filter boolean properties using equality operators",
                "properties": {
                    "property_name": {"type": "string"},
                    "operator": {"type": "string", "enum": ["=", "!="]},
                    "value": {"type": "boolean"}
                }
            },
            "integer_property_aggregation": {
                "type": "object",
                "description": "Aggregate numeric properties using statistical functions",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["COUNT", "TYPE", "MIN", "MAX", "MEAN", "MEDIAN", "MODE", "SUM"]}
                }
            },
            "text_property_aggregation": {
                "type": "object",
                "description": "Aggregate text properties using frequency analysis",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["COUNT", "TYPE", "TOP_OCCURRENCES"]},
                    "top_occurrences_limit": {"type": "integer"}
                }
            },
            "boolean_property_aggregation": {
                "type": "object",
                "description": "Aggregate boolean properties using statistical functions",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["COUNT", "TYPE", "TOTAL_TRUE", "TOTAL_FALSE", "PERCENTAGE_TRUE", "PERCENTAGE_FALSE"]}
                }
            },
            "groupby_property": {
                "type": "string",
                "description": "Group the results by a property."
            }
        }
    else:
        properties = {
            "collection_name": {
                "type": "string",
                "description": "A collection to search through.",
                "enum": collections_list
            },
            "search_query": {
                "type": "string",
                "description": "A search query"
            },
            "filter_string": {
                "type": "string",
                "description": "A filter to apply to the search results."
            },
            "aggregate_string": {
                "type": "string",
                "description": "An aggregation to apply to the search results."
            }
        }

    return OpenAITool(
        type="function",
        function=OpenAIFunction(
            name="query_database",
            description=f"""Query a database.

            Available collections in this database:
            {collections_description}""",
            parameters=OpenAIParameters(
                type="object",
                properties=properties,
                required=["tool_rationale", "collection_name"]
            )
        )
    )