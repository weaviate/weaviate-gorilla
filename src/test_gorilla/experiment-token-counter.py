#!/usr/bin/env python3

import json
import tiktoken
import requests
import os

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel

try:
    from src.utils.load_queries import load_queries
    from src.utils.weaviate_fc_utils import (
        get_collections_info,
        build_weaviate_query_tool_for_openai
    )
    from src.models import Tool, Function, Parameters, ParameterProperty
except ImportError:
    print("Warning: Could not import from src.* modules. Adjust import paths as needed.")

QUERIES_FILE = "../../data/synthetic-weaviate-queries-with-schemas.json"
MODEL = "gpt-4o"

def main():
    encoding = tiktoken.encoding_for_model(MODEL)

    print("=== Loading Weaviate Queries ===")
    weaviate_queries = load_queries(QUERIES_FILE)
    total_queries = len(weaviate_queries)
    print(f"Loaded {total_queries} queries.")

    total_prompt_tokens = 0
    total_tool_tokens = 0
    total_query_tokens = 0
    total_output_tokens = 0
    all_prompt_counts = 0

    current_schema_tool_tokens = []
    schema_tool_token_stats = []

    database_schema_index = 0

    print("=== Beginning Schema-by-Schema Count ===")

    collections_description = ""
    collections_enum = []

    for idx, query in enumerate(weaviate_queries):
        if idx == 0:
            class_schemas = weaviate_queries[0].database_schema.weaviate_collections
            for class_schema in class_schemas:
                schema_dict = {
                    'class': class_schema.name,
                    'description': class_schema.envisioned_use_case_overview,
                    'properties': []
                }
                for prop in class_schema.properties:
                    schema_dict['properties'].append({
                        'name': prop.name,
                        'description': prop.description,
                        'dataType': prop.data_type
                    })
                schema_dict['vectorizer'] = 'text2vec-transformers'
                schema_dict['vectorIndexType'] = 'hnsw'
            (collections_description, collections_enum) = mock_collections_info(class_schemas)

        if idx > 0 and idx % 64 == 0:
            if current_schema_tool_tokens:
                schema_tool_token_stats.append({
                    'schema_index': database_schema_index,
                    'min_tokens': min(current_schema_tool_tokens),
                    'max_tokens': max(current_schema_tool_tokens),
                    'avg_tokens': sum(current_schema_tool_tokens) / len(current_schema_tool_tokens)
                })
            current_schema_tool_tokens = []
            
            database_schema_index += 1
            class_schemas = weaviate_queries[idx].database_schema.weaviate_collections
            for class_schema in class_schemas:
                schema_dict = {
                    'class': class_schema.name,
                    'description': class_schema.envisioned_use_case_overview,
                    'properties': []
                }
                for prop in class_schema.properties:
                    schema_dict['properties'].append({
                        'name': prop.name,
                        'description': prop.description,
                        'dataType': prop.data_type
                    })
                schema_dict['vectorizer'] = 'text2vec-transformers'
                schema_dict['vectorIndexType'] = 'hnsw'
            (collections_description, collections_enum) = mock_collections_info(class_schemas)

        tool = Tool(
            type="function",
            function=Function(
                name="query_weaviate",
                description=f"Query the Weaviate database with the following collections:\n{collections_description}",
                parameters=Parameters(
                    type="object",
                    properties={
                        "collection_name": ParameterProperty(
                            type="string",
                            description="The name of the collection to query",
                            enum=collections_enum
                        ),
                        "search_query": ParameterProperty(
                            type="string",
                            description="Optional semantic search query"
                        ),
                        "integer_property_filter": ParameterProperty(
                            type="object",
                            description="Filter for integer properties"
                        ),
                        "text_property_filter": ParameterProperty(
                            type="object", 
                            description="Filter for text properties"
                        ),
                        "boolean_property_filter": ParameterProperty(
                            type="object",
                            description="Filter for boolean properties"
                        ),
                        "integer_property_aggregation": ParameterProperty(
                            type="object",
                            description="Aggregation for integer properties"
                        ),
                        "text_property_aggregation": ParameterProperty(
                            type="object",
                            description="Aggregation for text properties"
                        ),
                        "boolean_property_aggregation": ParameterProperty(
                            type="object",
                            description="Aggregation for boolean properties"
                        ),
                        "groupby_property": ParameterProperty(
                            type="string",
                            description="Property to group results by"
                        )
                    },
                    required=["collection_name"]
                )
            )
        )

        user_query = query.corresponding_natural_language_query

        tool_text = json.dumps(tool.model_dump(), indent=2, ensure_ascii=False)

        tool_part = f"System: You are an LLM that can call the function below.\n\nFunction specification:\n{tool_text}\n\n"
        query_part = f"User: {user_query}"
        
        tool_tokens = len(encoding.encode(tool_part))
        query_tokens = len(encoding.encode(query_part))
        prompt_tokens = tool_tokens + query_tokens

        mock_output = Tool(
            type="function",
            function=Function(
                name="query_weaviate",
                description=f"Query the Weaviate database with the following collections:\n{collections_description}",
                parameters=Parameters(
                    type="object",
                    properties={
                        "collection_name": ParameterProperty(
                            type="string",
                            description="The name of the collection to query",
                            enum=collections_enum
                        )
                    },
                    required=["collection_name"]
                )
            )
        )
        output_text = json.dumps(mock_output.model_dump(), ensure_ascii=False)
        output_tokens = len(encoding.encode(output_text))
        total_output_tokens += output_tokens

        current_schema_tool_tokens.append(tool_tokens)

        total_tool_tokens += tool_tokens
        total_query_tokens += query_tokens
        total_prompt_tokens += prompt_tokens
        all_prompt_counts += 1

        print(f"Query {idx+1}/{total_queries}:")
        print(f"  Tool tokens: {tool_tokens}")
        print(f"  Query tokens: {query_tokens}")
        print(f"  Output tokens: {output_tokens}")
        print(f"  Total tokens: {prompt_tokens + output_tokens}")

    if current_schema_tool_tokens:
        schema_tool_token_stats.append({
            'schema_index': database_schema_index,
            'min_tokens': min(current_schema_tool_tokens),
            'max_tokens': max(current_schema_tool_tokens),
            'avg_tokens': sum(current_schema_tool_tokens) / len(current_schema_tool_tokens)
        })

    avg_prompt_tokens = 0
    avg_tool_tokens = 0
    avg_query_tokens = 0
    avg_output_tokens = 0
    if all_prompt_counts > 0:
        avg_prompt_tokens = total_prompt_tokens / all_prompt_counts
        avg_tool_tokens = total_tool_tokens / all_prompt_counts
        avg_query_tokens = total_query_tokens / all_prompt_counts
        avg_output_tokens = total_output_tokens / all_prompt_counts

    print("\n=== TOKEN COUNT SUMMARY ===")
    print(f"Total queries processed: {all_prompt_counts}")
    print(f"Total tool tokens: {total_tool_tokens}")
    print(f"Total query tokens: {total_query_tokens}")
    print(f"Total prompt tokens: {total_prompt_tokens}")
    print(f"Total output tokens: {total_output_tokens}")
    print(f"Average tool tokens per prompt: {avg_tool_tokens:.1f}")
    print(f"Average query tokens per prompt: {avg_query_tokens:.1f}")
    print(f"Average output tokens per prompt: {avg_output_tokens:.1f}")
    print(f"Average total tokens per prompt: {avg_prompt_tokens + avg_output_tokens:.1f}")

    print("\n=== PER-SCHEMA TOOL TOKEN STATS ===")
    for stats in schema_tool_token_stats:
        print(f"\nSchema {stats['schema_index']}:")
        print(f"  Tool tokens: {stats['avg_tokens']}")

def mock_collections_info(class_schemas):
    desc_parts = []
    enum_list = []
    for cls in class_schemas:
        desc_parts.append(f"Class {cls.name}:\n  {cls.envisioned_use_case_overview}")
        for prop in cls.properties:
            desc_parts.append(f"  Property {prop.name} ({prop.data_type}): {prop.description}")
        enum_list.append(cls.name)
    full_desc = "\n".join(desc_parts)
    return (full_desc, enum_list)

if __name__ == "__main__":
    main()
