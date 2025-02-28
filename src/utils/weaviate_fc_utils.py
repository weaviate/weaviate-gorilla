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

def get_collections_info(client):
    """Get information about collections for building tools."""
    try:
        # Get the schema using schema.get() instead of collections.get()
        schema = client.schema.get()
        
        # Extract collection names
        collections_enum = []
        collections_description = "Available collections:\n"
        
        if 'classes' in schema:
            for cls in schema['classes']:
                collection_name = cls['class']
                collections_enum.append(collection_name)
                
                # Add collection info to description
                collections_description += f"- {collection_name}: {cls.get('description', 'No description')}\n"
                collections_description += "  Properties:\n"
                
                # Add property info to description
                for prop in cls.get('properties', []):
                    prop_name = prop['name']
                    prop_type = prop['dataType']
                    prop_desc = prop.get('description', 'No description')
                    collections_description += f"  - {prop_name} ({prop_type}): {prop_desc}\n"
                
                collections_description += "\n"
        
        return collections_description, collections_enum
    
    except Exception as e:
        print(f"Error getting collections info: {str(e)}")
        return "Error retrieving schema", []

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
                "metrics": {"type": "string", "enum": ["MIN", "MAX", "MEAN", "MEDIAN", "MODE", "SUM"]}
            }
        },
        "text_property_aggregation": {
            "type": "object",
            "description": "Aggregate text properties using frequency analysis",
            "properties": {
                "property_name": {"type": "string"},
                "metrics": {"type": "string", "enum": ["TOP_OCCURRENCES"]},
                "top_occurrences_limit": {"type": "integer"}
            }
        },
        "boolean_property_aggregation": {
            "type": "object",
            "description": "Aggregate boolean properties using statistical functions",
            "properties": {
                "property_name": {"type": "string"},
                "metrics": {"type": "string", "enum": ["TOTAL_TRUE", "TOTAL_FALSE", "PERCENTAGE_TRUE", "PERCENTAGE_FALSE"]}
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
                "metrics": {"type": "string", "enum": ["MIN", "MAX", "MEAN", "MEDIAN", "MODE", "SUM"]}
            }
        },
        "text_property_aggregation": {
            "type": "object",
            "description": "Aggregate text properties using frequency analysis",
            "properties": {
                "property_name": {"type": "string"},
                "metrics": {"type": "string", "enum": ["TOP_OCCURRENCES"]},
                "top_occurrences_limit": {"type": "integer"}
            }
        },
        "boolean_property_aggregation": {
            "type": "object",
            "description": "Aggregate boolean properties using statistical functions",
            "properties": {
                "property_name": {"type": "string"},
                "metrics": {"type": "string", "enum": ["TOTAL_TRUE", "TOTAL_FALSE", "PERCENTAGE_TRUE", "PERCENTAGE_FALSE"]}
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
                    "metrics": {"type": "string", "enum": ["MIN", "MAX", "MEAN", "MEDIAN", "MODE", "SUM"]}
                },
                "required": ["property_name", "metrics"]
            },
            "text_property_aggregation": {
                "type": "object",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["TOP_OCCURRENCES"]},
                    "top_occurrences_limit": {"type": "integer"}
                },
                "required": ["property_name", "metrics"]
            },
            "boolean_property_aggregation": {
                "type": "object",
                "properties": {
                    "property_name": {"type": "string"},
                    "metrics": {"type": "string", "enum": ["TOTAL_TRUE", "TOTAL_FALSE", "PERCENTAGE_TRUE", "PERCENTAGE_FALSE"]}
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
                "metrics": {"type": "string", "enum": ["MIN", "MAX", "MEAN", "MEDIAN", "MODE", "SUM"]}
            }
        },
        "text_property_aggregation": {
            "type": "object",
            "description": "Aggregate text properties using frequency analysis",
            "properties": {
                "property_name": {"type": "string"},
                "metrics": {"type": "string", "enum": ["TOP_OCCURRENCES"]},
                "top_occurrences_limit": {"type": "integer"}
            }
        },
        "boolean_property_aggregation": {
            "type": "object",
            "description": "Aggregate boolean properties using statistical functions",
            "properties": {
                "property_name": {"type": "string"},
                "metrics": {"type": "string", "enum": ["TOTAL_TRUE", "TOTAL_FALSE", "PERCENTAGE_TRUE", "PERCENTAGE_FALSE"]}
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
                "metrics": {"type": "string", "enum": ["MIN", "MAX", "MEAN", "MEDIAN", "MODE", "SUM"]}
            }
        },
        "text_property_aggregation": {
            "type": "object",
            "description": "Aggregate text properties using frequency analysis",
            "properties": {
                "property_name": {"type": "string"},
                "metrics": {"type": "string", "enum": ["TOP_OCCURRENCES"]},
                "top_occurrences_limit": {"type": "integer"}
            }
        },
        "boolean_property_aggregation": {
            "type": "object",
            "description": "Aggregate boolean properties using statistical functions",
            "properties": {
                "property_name": {"type": "string"},
                "metrics": {"type": "string", "enum": ["TOTAL_TRUE", "TOTAL_FALSE", "PERCENTAGE_TRUE", "PERCENTAGE_FALSE"]}
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