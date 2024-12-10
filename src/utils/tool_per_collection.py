from typing import List
from src.models import OpenAITool, OpenAIFunction, OpenAIParameters

def build_one_tool_per_collection(collections_description: str, collections_list: list[str], generate_with_models: bool = False) -> List[OpenAITool]:
    """
    Creates a separate query tool for each collection in the database.
    
    Args:
        collections_description: String describing all collections
        collections_list: List of collection names
        generate_with_models: Whether to use structured models for parameters
        
    Returns:
        List of OpenAITool objects, one per collection
    """
    tools = []
    
    # Split the collections description into sections per collection
    collection_sections = collections_description.split("\nCollection Name: ")[1:]
    collection_descriptions = {
        section.split("\n")[0]: "\n".join(section.split("\n")[1:])
        for section in collection_sections
    }
    
    for collection_name in collections_list:
        if generate_with_models:
            properties = {
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

        tool = OpenAITool(
            type="function",
            function=OpenAIFunction(
                name=f"query_{collection_name}",
                description=f"""Query the {collection_name} collection.
                
                Collection details:
                {collection_descriptions.get(collection_name, '')}""",
                parameters=OpenAIParameters(
                    type="object",
                    properties=properties,
                    required=[]
                )
            )
        )
        tools.append(tool)
    
    return tools
