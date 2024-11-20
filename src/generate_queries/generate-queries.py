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
from src.utils.util import pretty_print_weaviate_query

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
Given a user's database schema write a natural language command that requires using ALL of the following query operators provided to be answered correctly:

{operator_description}

The query must require ALL of these provided query operators - do not include operators that aren't strictly necessary.
For search queries, remember these are for semantic similarity search, not exact text matching which can be done with text property filters.

[[ database schema ]]
{database_schema}

Please respond with a natural language query that requires all the specified operators.
"""

with open("../../data/3-collection-schemas-with-search-property.json", "r") as json_file:
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
    print(f"Creating queries for database schema: {idx}")
    print(f"\n\033[1mRunning for {time.time() - start} seconds.\033[0m\n")
    
    # Generate all combinations of operators
    for search, filter_, agg, group in itertools.product(
        search_options, filter_options, aggregation_options, groupby_options
    ):
        # Skip if all are None
        if not any([search, filter_, agg, group]):
            continue
            
        # Build properties dict for dynamic model
        properties = {
            "target_collection": (str, Field(..., description="The name of the Weaviate collection to query")),
            "reflection_of_APIs_that_will_be_used_in_this_query": (str, Field(..., description="A description of which Weaviate APIs will be needed to execute this query")),
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

        '''
        # Future work, would like to wait until there is data in the collections to better ground this.
        properties["scenario_that_specifically_requires_this_exact_information"] = (
            str,
            Field(..., description="A real-world use case that would require this specific combination of query operators and their values. This should describe a concrete business scenario or analytical need that would specifically require using these exact query parameters together, including any specific numeric thresholds or values. For example, if the query uses a price filter of $20, explain why that exact price point is significant rather than just describing a general need for price filtering. The scenario should demonstrate why these precise parameters were chosen and why different values or simpler query combinations would not suffice for this specific use case.")
        )
        '''

        properties["corresponding_natural_language_query"] = (
            str, 
            Field(..., description="The natural language question that this query is designed to answer. The question MUST be phrased in a way that explicitly requires using all of the specified query operators - it should not be answerable without using every operator that was selected")
        )

        # Create dynamic model
        DynamicQueryModel = create_model('DynamicQueryModel', **properties)
        
        # Generate query using LM
        task_instructions = create_query_prompt.format(
            operator_description="\n".join(operator_desc),
            database_schema=format_schema(database_schema)
        )
        
        query = lm_service.generate(task_instructions, DynamicQueryModel)
        query_dict = query.model_dump()
        
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
        print("\n\033[96mQuery Parameters Used:\033[0m")
        print(f"  \033[96mSearch:\033[0m {search}")
        print(f"  \033[96mFilter:\033[0m {filter_}")
        print(f"  \033[96mAggregation:\033[0m {agg}")
        print(f"  \033[96mGroup By:\033[0m {group}")
        print("="*50)
        print(f"\033[96mGenerated query:\033[0m")
        pretty_print_weaviate_query(weaviate_query)
        print("\033[96mMore abstract scenario:\033[0m")
        '''
        print(query_dict["scenario_that_specifically_requires_this_exact_information"])
        '''
        
    print(f"\n\033[92mCreated {len(results)} queries for this schema.\033[0m\n")

# Save results with schemas
with open("synthetic-weaviate-queries-with-schemas.json", "w") as file:
    json.dump(results, file, indent=4)

# Generate table rows from results
markdown_table = '''
| Search Query | Filter | Aggregation | Group By | Natural Language Command |
|-------------|--------|-------------|----------|-------------------------|
'''

# Get first schema's results
first_schema_results = [r for r in results if r["database_schema"] == results[0]["database_schema"]]

for result in first_schema_results:
    query = result["query"]
    search = "✓" if query.get("search_query") else ""
    filter_type = next((k.replace("_property_filter","") for k in ["integer_property_filter", "text_property_filter", "boolean_property_filter"] if query.get(k)), "")
    agg_type = next((k.replace("_property_aggregation","") for k in ["integer_property_aggregation", "text_property_aggregation", "boolean_property_aggregation"] if query.get(k)), "")
    group = "✓" if query.get("groupby_property") else ""
    nl_command = query.get("corresponding_natural_language_query", "").replace("|","/")[:100] + "..."
    
    markdown_table += f"| {search} | {filter_type} | {agg_type} | {group} | {nl_command} |\n"

# Save markdown table to file
with open("query_summary_table_single_collection.md", "w") as f:
    f.write(markdown_table)