import json
import itertools
from typing import Optional
from pydantic import create_model, Field
from src.lm.lm import LMService
from src.vectorizer.vectorizer import VectorizerService
from src.models import (
    WeaviateQuery,
    IntPropertyFilter,
    TextPropertyFilter, 
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation
)

from src.generate_queries.api_descriptions import (
    search_query,
    int_property_filter,
    text_property_filter,
    boolean_property_filter,
    int_property_aggregation,
    text_property_aggregation,
    boolean_property_aggregation,
    groupby
)

openai_api_key = ""

lm_service = LMService(
    model_provider = "openai",
    model_name = "gpt-4o",
    api_key = openai_api_key
)

lm_service.connection_test()

vectorizer_service = VectorizerService(
    model_provider = "openai",
    model_name = "text-embedding-3-small",
    api_key = openai_api_key
)

vectorizer_service.connection_test()

create_query_prompt = """
Given a user's database schema write a natural language command that requires using ALL of the following query operators to be answered correctly:

{operator_description}

The query must require ALL of these operators - do not include operators that aren't strictly necessary.
For search queries, remember these are for semantic similarity search, not exact text matching which can be done with text property filters.

[[ database schema ]]
{database_schema}

Please respond with a natural language query that requires all the specified operators.
"""

with open("../../data/simple-3-collection-schemas.json", "r") as json_file:
    database_schemas = json.load(json_file)

def format_schema(schema):
    return json.dumps(schema, indent=2)

# Define possible operators for each category
search_options = [("search_query", str), None]
filter_options = [
    ("integer_property_filter", IntPropertyFilter),
    ("text_property_filter", TextPropertyFilter),
    ("boolean_property_filter", BooleanPropertyFilter),
    None
]
aggregation_options = [
    ("integer_property_aggregation", IntAggregation),
    ("text_property_aggregation", TextAggregation),
    ("boolean_property_aggregation", BooleanAggregation),
    None
]
groupby_options = [("groupby_property", str), None]

results = []

import time
start = time.time()

for idx, database_schema in enumerate(database_schemas):
    if idx > 4:
        break
    print(f"\n\033[1mRunning for {time.time() - start} seconds.\033[0m\n")
    print(f"\033[96mWriting queries for database {idx+1}:\033[0m")
    print(f"{database_schema}\n\n")
    
    # Generate all combinations of operators
    for search, filter_, agg, group in itertools.product(
        search_options, filter_options, aggregation_options, groupby_options
    ):
        # Skip if all are None
        if not any([search, filter_, agg, group]):
            continue
            
        # Build properties dict for dynamic model
        properties = {
            "corresponding_natural_language_query": (str, ...),
            "target_collection": (str, ...)
        }
        
        # Build operator description for prompt
        operator_desc = []
        
        if search:
            properties[search[0]] = (search[1], ...)
            operator_desc.append(search_query)
            
        if filter_:
            properties[filter_[0]] = (filter_[1], ...)
            if filter_[0] == "integer_property_filter":
                operator_desc.append(int_property_filter)
            elif filter_[0] == "text_property_filter":
                operator_desc.append(text_property_filter)
            else:
                operator_desc.append(boolean_property_filter)
                
        if agg:
            properties[agg[0]] = (agg[1], ...)
            if agg[0] == "integer_property_aggregation":
                operator_desc.append(int_property_aggregation)
            elif agg[0] == "text_property_aggregation":
                operator_desc.append(text_property_aggregation)
            else:
                operator_desc.append(boolean_property_aggregation)
                
        if group:
            properties[group[0]] = (group[1], ...)
            operator_desc.append(groupby)

        # Create dynamic model
        DynamicQueryModel = create_model('DynamicQueryModel', **properties)
        print(DynamicQueryModel)
        
        # Generate query using LM
        task_instructions = create_query_prompt.format(
            operator_description="\n".join(operator_desc),
            database_schema=format_schema(database_schema)
        )
        
        query = lm_service.generate(task_instructions, DynamicQueryModel)
        query_dict = query.dict()
        
        # Convert to WeaviateQuery
        weaviate_query = WeaviateQuery(
            corresponding_natural_language_query=query_dict["corresponding_natural_language_query"],
            target_collection=query_dict["target_collection"],
            search_query=query_dict.get("search_query"),
            integer_property_filter=query_dict.get("integer_property_filter"),
            text_property_filter=query_dict.get("text_property_filter"),
            boolean_property_filter=query_dict.get("boolean_property_filter"),
            integer_property_aggregation=query_dict.get("integer_property_aggregation"),
            text_property_aggregation=query_dict.get("text_property_aggregation"),
            boolean_property_aggregation=query_dict.get("boolean_property_aggregation"),
            groupby_property=query_dict.get("groupby_property")
        )
        
        # Store result with schema
        results.append({
            "database_schema": database_schema,
            "query": weaviate_query.model_dump()
        })
        print(f"\033[96mGenerated query: {weaviate_query}\n\033[0m")

    print(f"\n\033[92mCreated {len(results)} queries for this schema.\033[0m\n")

# Save results with schemas
with open("synthetic-weaviate-queries-with-schemas.json", "w") as file:
    json.dump(results, file, indent=4)