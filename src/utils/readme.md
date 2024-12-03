### The Weaviate API currently in our PR to the Berkeley Gorilla APIZoo is based on this schema:

```python
def build_weaviate_query_tool_for_openai(collections_description: str, collections_list: list[str]) -> OpenAITool:
      properties = {
            "collection_name": {
                "type": "string",
                "description": "The collection to query. Has a boolean-valued property `inBoston` that you can use to filter queries on if useful.",
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
```python
