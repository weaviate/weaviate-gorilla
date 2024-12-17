import weaviate
from src.models import (
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation,
    GroupBy
)
from src.models import (
    OpenAIParameters,
    OpenAIFunction,
    OpenAITool,
    AnthropicTool,
    AnthropicToolInputSchema,
    OllamaFunctionParameters,
    OllamaFunction,
    OllamaTool,
    CohereFunctionParameters,
    CohereFunction,
    CohereTool,
    TogetherAITool,
    TogetherAIFunction,
    TogetherAIParameters
)
import re
from typing import Tuple, Union, Any, Dict, List
from pydantic import BaseModel
from typing import Literal, Optional

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
            # output.append(f"- {prop.name}: {prop.description} (type: {prop.data_type.value})")
            # because of 1024 token limit :(
            output.append(f"- {prop.name}: (type: {prop.data_type.value})")

    return "\n".join(output), collection_names

def build_weaviate_query_tool_for_openai(collections_description: str, collections_list: list[str]) -> OpenAITool:
    properties = {
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
                required=["collection_name"]
            )
        )
    )

def build_weaviate_query_tool_for_anthropic(collections_description: str, collections_list: list[str]) -> AnthropicTool:
    properties = {
        "collection_name": {
            "type": "string",
            "description": "The collection to query",
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

    return AnthropicTool(
        name="query_database",
        description=f"""Query a database.

        Available collections in this database:
        {collections_description}""",
        input_schema=AnthropicToolInputSchema(
            type="object",
            properties=properties,
            required=["collection_name"]
        )
    )

def build_weaviate_query_tool_for_ollama(collections_description: str, collections_list: list[str]) -> OllamaTool:
    query_parameters = {
        "type": "object",
        "properties": {
            "collection_name": {
                "type": "string",
                "enum": collections_list
            },
            "search_query": {
                "type": "string"
            },
            "integer_property_filter": {
                "type": "object",
                "properties": {
                    "property_name": {"type": "string"},
                    "operator": {"type": "string", "enum": ["=", "<", ">", "<=", ">="]},
                    "value": {"type": "integer"}
                },
                "required": ["property_name", "operator", "value"]
            },
            "text_property_filter": {
                "type": "object", 
                "properties": {
                    "property_name": {"type": "string"},
                    "operator": {"type": "string", "enum": ["=", "LIKE"]},
                    "value": {"type": "string"}
                },
                "required": ["property_name", "operator", "value"]
            },
            "boolean_property_filter": {
                "type": "object",
                "properties": {
                    "property_name": {"type": "string"},
                    "operator": {"type": "string", "enum": ["="]},
                    "value": {"type": "boolean"}
                },
                "required": ["property_name", "operator", "value"]
            },
            "integer_property_aggregation": {
                "type": "object",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["COUNT", "TYPE", "MIN", "MAX", "MEAN", "MEDIAN", "MODE", "SUM"]}
                },
                "required": ["property_name", "metrics"]
            },
            "text_property_aggregation": {
                "type": "object",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["COUNT", "TYPE", "TOP_OCCURRENCES"]},
                    "top_occurrences_limit": {"type": "integer"}
                },
                "required": ["property_name", "metrics"]
            },
            "boolean_property_aggregation": {
                "type": "object",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["COUNT", "TYPE", "TOTAL_TRUE", "TOTAL_FALSE", "PERCENTAGE_TRUE", "PERCENTAGE_FALSE"]}
                },
                "required": ["property_name", "metrics"]
            },
            "groupby_property": {
                "type": "string"
            }
        },
        "required": ["collection_name"]
    }

    query_function = OllamaFunction(
        name="query_database",
        description=f"""Query a database.

        Available collections in this database:
        {collections_description}""",
        parameters=query_parameters
    )
    return OllamaTool(
        function=query_function
    )

def build_weaviate_query_tool_for_cohere(collections_description: str, collections_list: list[str]) -> CohereTool:
    properties = {
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

    return CohereTool(
        type="function",
        function=CohereFunction(
            name="query_database",
            description=f"""Query a database.

            Available collections in this database:
            {collections_description}""",
            parameters=CohereFunctionParameters(
                type="object",
                properties=properties,
                required=["collection_name"]
            )
        )
    )

def build_weaviate_query_tool_for_together(collections_description: str, collections_list: list[str]) -> TogetherAITool:
    properties = {
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

    return TogetherAITool(
        type="function",
        function=TogetherAIFunction(
            name="query_database",
            description=f"""Query a database.

            Available collections in this database:
            {collections_description}""",
            parameters=TogetherAIParameters(
                type="object",
                properties=properties,
                required=["collection_name"]
            )
        )
    )