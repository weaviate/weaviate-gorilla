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

search_query = """Use `search_query` when you need to find the most relevant results to a natural language query, especially in cases where property filters alone cannot capture user intent or when you want to enhance filtered results with semantic understanding. Unlike exact property filters (such as `text_property_filter`, `int_property_filter`, or `boolean_property_filter`), which require precise matches on property values, `search_query` interprets the meaning behind the words, handling synonyms, context, misspellings, and related concepts.

**Examples of when to use `search_query`:**

1. **Synonyms and Related Terms**: If a user searches for "energy-efficient refrigerators," a simple text filter on the product description may miss items labeled as "eco-friendly fridges." `search_query` understands that "energy-efficient" and "eco-friendly" are related concepts, and "refrigerators" and "fridges" are synonyms, thus returning more comprehensive results.

2. **Natural Language Questions**: When a user asks, "What laptops are good for gaming and under $1,000?" filters alone may struggle to interpret this multi-faceted query. `search_query` can parse the intent, understanding that the user wants gaming-capable laptops within a specific price range, even if those exact phrases aren't in the product properties.

3. **Misspellings and Variations**: A search for "wireless headphonez" with a misspelling may yield no results using exact filters. `search_query` can recognize and correct misspellings, returning relevant results for "wireless headphones."

4. **Contextual Understanding**: If a user searches for "comfortable chairs for back pain," filters might not capture the nuance unless there's a specific property labeled "suitable for back pain." `search_query` can semantically match products designed to alleviate back discomfort, even if the exact terms don't match.

5. **Enhancing Filtered Results**: You can combine `search_query` with property filters to refine results further. For example, after applying an `int_property_filter` to select houses with "price < $500,000," you can use `search_query` with "family-friendly neighborhood with good schools" to find listings that match both the filter and the semantic intent.

In situations where user queries are complex, involve synonyms, or require an understanding of context and intent beyond exact property matches, `search_query` is the ideal choice. It excels at capturing the essence of what the user is looking for, providing relevant results that property filters or aggregations alone cannot achieve."""

text_property_filter = """Use `text_property_filter` when you need to retrieve objects that match a specific condition on a text-valued property with exact or pattern-based matching. Unlike `search_query`, which handles natural language input and semantic matching to capture user intent, `text_property_filter` strictly matches the specified text condition without interpreting synonyms or context. This makes it ideal for precise filtering tasks, such as retrieving all items with the category 'Electronics'. If you require exact matching on a text property rather than semantic relevance or data aggregation (as provided by `text_property_aggregation`), `text_property_filter` is the appropriate API to use."""

int_property_filter = """Use `int_property_filter` when you need to return objects that match a specific numerical condition on an integer-valued property, such as finding all products with a price less than $100. Unlike `search_query`, which is designed for semantic matching based on user intent, `int_property_filter` provides precise numerical filtering without interpreting natural language queries or semantic meaning. This API is ideal when exact numerical conditions are required. If your goal is to filter data based on specific integer values or ranges rather than semantic search or data aggregation (as offered by `int_property_aggregation`), `int_property_filter` is the suitable choice."""

boolean_property_filter = """Use `boolean_property_filter` when you need to retrieve objects that match a specific true or false condition on a boolean-valued property, such as selecting all users who are 'subscribed' or items that are 'in stock'. Unlike `search_query`, which interprets natural language input to find semantically relevant results, `boolean_property_filter` strictly filters records based on the exact true or false value of a property. This API does not handle synonyms, context, or fuzzy matching. If you need precise filtering based on a boolean property rather than semantic search or aggregation (as provided by `boolean_property_aggregation`), `boolean_property_filter` is the appropriate API to use."""

text_property_aggregation = """Use `text_property_aggregation` when you need to compute aggregate values over a text-valued property, such as counting the number of items in each category or listing all unique tags associated with products. Unlike `search_query`, which retrieves individual records based on semantic relevance to a query, `text_property_aggregation` provides summary information over text properties without retrieving individual records. This API does not handle natural language input or fuzzy matching. If your goal is to generate reports or insights by aggregating text data rather than searching or filtering for specific records (as done with `text_property_filter`), `text_property_aggregation` is the suitable API to use."""

int_property_aggregation = """Use `int_property_aggregation` when you need to perform aggregate calculations over an integer-valued property, such as computing the average price of items, total sales, or maximum score. Unlike `search_query`, which focuses on retrieving relevant records based on user intent and semantic meaning, `int_property_aggregation` provides numerical insights over a dataset without processing natural language queries or retrieving individual records. If you require numerical summaries and statistics over integer data rather than searching or filtering (as with `int_property_filter`), `int_property_aggregation` is the appropriate API to use."""

boolean_property_aggregation = """Use `boolean_property_aggregation` when you need to aggregate data over a boolean-valued property, such as counting the number of items that are 'in stock' versus 'out of stock' or determining the percentage of users who are 'verified'. Unlike `search_query`, which retrieves results based on semantic understanding, `boolean_property_aggregation` provides summary statistics over boolean properties without processing natural language input or retrieving individual records. If your objective is to gain insights by aggregating boolean data rather than searching or filtering specific records (as done with `boolean_property_filter`), `boolean_property_aggregation` is the suitable API to use."""

groupby = """Use `groupby` when you need to organize or segment results based on the values of a specific property, creating groups of records that share the same property value. For example, grouping sales data by region or products by category. Unlike `search_query`, which retrieves relevant records based on semantic queries, `groupby` reorganizes the dataset without interpreting natural language or semantic meaning. It does not filter out records like property filters (e.g., `text_property_filter`, `int_property_filter`, `boolean_property_filter`) nor does it perform aggregate computations unless combined with aggregation functions. If you need to segment your data into groups based on property values rather than searching, filtering, or aggregating data, `groupby` is the appropriate API to use."""

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

query_count = 0
for idx, database_schema in enumerate(database_schemas):
    if idx > 0:  # Only process first schema
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
        
        query_count += 1
        if query_count >= 2:  # Break after 2 queries
            break
            
    if query_count >= 2:  # Break outer loop too
        break
            
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
    nl_command = query.get("corresponding_natural_language_query")
    
    markdown_table += f"| {search} | {filter_type} | {agg_type} | {group} | {nl_command} |\n"

# Save markdown table to file
with open("query_summary_table_single_collection.md", "w") as f:
    f.write(markdown_table)