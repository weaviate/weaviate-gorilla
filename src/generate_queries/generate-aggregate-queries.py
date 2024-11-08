from src.models import SyntheticAggregationQueries
from src.create.create import CreateObjects
from src.lm.lm import LMService
from src.vectorizer.vectorizer import VectorizerService
import json

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


# Load schemas from JSON
with open("./data/simple-3-collection-schemas.json", "r") as json_file:
    database_schemas = json.load(json_file)

# Describe Aggregate DSL

description="""
aggregate expression

Basic property aggregation syntax: property_name:aggregation_type

Group by syntax: GROUP_BY(property_name)
- Note: Currently limited to one property or cross-reference. Nested paths are not supported.

Available Aggregation Types
Based on data type:

Text Properties
- COUNT
- TYPE
- TOP_OCCURRENCES[limit] - Optional limit parameter for minimum count

Numeric Properties (Number/Integer)
- COUNT
- TYPE
- MIN
- MAX
- MEAN
- MEDIAN
- MODE
- SUM

Boolean Properties
- COUNT
- TYPE
- TOTAL_TRUE
- TOTAL_FALSE
- PERCENTAGE_TRUE
- PERCENTAGE_FALSE

Date Properties
- COUNT
- TYPE
- MIN
- MAX
- MEAN
- MEDIAN
- MODE

Examples

Simple Aggregations

# Count all records in the collection
Article:COUNT

# Get wordCount (TEXT property) statistics
wordCount:COUNT,wordCount:MEAN,wordCount:MAX

# Get top occurrences of categories (TEXT property) with minimum count of 5
category:TOP_OCCURRENCES[5]

Grouped Aggregations

# Group by publication and get counts
GROUP_BY(publication):COUNT

# Group by category with multiple metrics
GROUP_BY(category):COUNT,price:MEAN,price:MAX

## Combining Multiple Aggregations
Multiple aggregations can be combined using comma separation:

GROUP_BY(publication):COUNT,wordCount:MEAN,category:TOP_OCCURRENCES[5]
"""

# Prepare the prompt template
create_single_hop_query_prompt = """
Given a user's database schema write a natural language commands simulating cases where the user would want to use a filter to retrieve data objects matching conditions applied to TEXT-, INT-, and BOOLEAN-valued properties.

[[ database schema ]]
{database_schema}

[[ natural language command ]]
"""

def format_schema(schema):
    # Format the schema for inclusion in the prompt
    return json.dumps(schema, indent=2)

synthetic_queries = []

for database_schema in database_schemas:
    task_instructions = create_single_hop_query_prompt.format(
        database_schema=format_schema(database_schema)
    )
        
    # Generate the synthetic query
    queries = CreateObjects(
        num_samples=1,
        task_instructions=task_instructions,
        output_model=SyntheticAggregationQueries,
        lm_service=lm_service,
        vectorizer_service=vectorizer_service,
        dedup_strategy="none"  # No deduplication needed for single samples
    )[0]
    print(queries)
    
    synthetic_queries.append({
        "database_schema": database_schema,
        "metadata": "INT AGGREGATION", 
        "property_name": queries.int_aggregation_query.property_name,
        "metrics": queries.int_aggregation_query.metrics,
        "query": queries.int_aggregation_query.corresponding_natural_language_query
    })

    synthetic_queries.append({
        "database_schema": database_schema,
        "metadata": "TEXT AGGREGATION",
        "property_name": queries.text_aggregation_query.property_name,
        "metrics": queries.text_aggregation_query.metrics,
        "query": queries.text_aggregation_query.corresponding_natural_language_query
    })

    synthetic_queries.append({
        "database_schema": database_schema,
        "metadata": "BOOLEAN AGGREGATION",
        "property_name": queries.boolean_aggregation_query.property_name,
        "metrics": queries.boolean_aggregation_query.metrics,
        "query": queries.boolean_aggregation_query.corresponding_natural_language_query
    })

# Save the synthetic queries to a file
with open("synthetic-aggregation-queries.json", "w") as file:
    json.dump(synthetic_queries, file, indent=4)
