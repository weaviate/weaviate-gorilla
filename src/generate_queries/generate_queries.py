import json
import itertools
from typing import Optional, List, Dict
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
import os

# Export operator descriptions
search_query_desc = """Use `search_query` when you need to find the most relevant results..."""

text_property_filter_desc = """Use `text_property_filter` when you need to retrieve objects..."""

int_property_filter_desc = """Use `int_property_filter` when you need to return objects..."""

boolean_property_filter_desc = """Use `boolean_property_filter` when you need to retrieve objects..."""

text_property_aggregation_desc = """Use `text_property_aggregation` when you need to compute aggregate values..."""

int_property_aggregation_desc = """Use `int_property_aggregation` when you need to perform aggregate calculations..."""

boolean_property_aggregation_desc = """Use `boolean_property_aggregation` when you need to aggregate data..."""

groupby_desc = """Use `groupby` when you need to organize or segment results..."""

def init_services(api_key: str) -> tuple[LMService, VectorizerService]:
    """Initialize LM and Vectorizer services."""
    lm_service = LMService(
        model_provider="openai",
        model_name="gpt-4o",
        api_key=api_key
    )
    
    vectorizer_service = VectorizerService(
        model_provider="openai",
        model_name="text-embedding-3-small",
        api_key=api_key
    )
    
    return lm_service, vectorizer_service

def format_schema(schema: Dict) -> str:
    """Format schema as pretty-printed JSON string."""
    return json.dumps(schema, indent=2)

def get_query_prompt() -> str:
    """Get the base query generation prompt."""
    return """
Write a natural language database query command that meets these STRICT requirements:

1. The query MUST require using ALL of these specific operators to be answered correctly:

{operator_description}

2. The query MUST be impossible to answer correctly without using EVERY operator listed above. Each operator must be essential for answering the query.

3. The query MUST NOT require or benefit from using any operators that weren't listed above. A query that could be better answered by adding other operators is incorrect.

For example:
- If semantic search is listed: The query should require finding similar concepts, not exact text matches
- If aggregation is listed: The query should require computing summary statistics
- If grouping is listed: The query should require segmenting/organizing results
- If filtering is listed: The query should require exact matching on specific properties

[[ database schema ]]
{database_schema}

Your task is to write ONE natural language query where:
- Using ALL the listed operators is necessary
- Using ONLY the listed operators is sufficient
- Adding any other operators would not improve the answer

Bad example (if only search and text filtering are listed):
"Find employees who work in engineering and calculate their average salary"
This requires aggregation which wasn't listed.

Good example (if only search and text filtering are listed):
"Find employees whose job descriptions are similar to 'machine learning' and who work in the engineering department"
This requires semantic search for job matching and text filtering for department.
"""

def generate_single_query(
    schema: Dict,
    search: Optional[tuple] = None,
    filter_: Optional[tuple] = None,
    agg: Optional[tuple] = None,
    group: Optional[tuple] = None,
    lm_service: Optional[LMService] = None
) -> Dict:
    """Generate a single query with the specified combination of operators."""
    
    # Build properties dict for dynamic model
    properties = {
        "target_collection": (str, Field(..., description="The name of the Weaviate collection to query")),
        "reflection_of_APIs_that_will_be_used_in_this_query": (
            str, 
            Field(..., description="A description of which Weaviate APIs will be needed to execute this query")
        ),
    }
    
    # Build operator description for prompt
    operator_desc = []
    
    if search:
        properties[search[0]] = (search[1], ...)
        operator_desc.append(search_query_desc)
        
    if filter_:
        properties[filter_[0]] = (filter_[1], ...)
        if filter_[0] == "integer_property_filter":
            operator_desc.append(int_property_filter_desc)
        elif filter_[0] == "text_property_filter":
            operator_desc.append(text_property_filter_desc)
        else:
            operator_desc.append(boolean_property_filter_desc)
            
    if agg:
        properties[agg[0]] = (agg[1], ...)
        if agg[0] == "integer_property_aggregation":
            operator_desc.append(int_property_aggregation_desc)
        elif agg[0] == "text_property_aggregation":
            operator_desc.append(text_property_aggregation_desc)
        else:
            operator_desc.append(boolean_property_aggregation_desc)
            
    if group:
        properties[group[0]] = (group[1], ...)
        operator_desc.append(groupby_desc)

    properties["corresponding_natural_language_query"] = (
        str, 
        Field(..., description="The natural language question that this query is designed to answer.")
    )

    # Create dynamic model
    DynamicQueryModel = create_model('DynamicQueryModel', **properties)
    
    # Generate query using LM
    task_instructions = get_query_prompt().format(
        operator_description="\n".join(operator_desc),
        database_schema=format_schema(schema)
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
    
    return weaviate_query.model_dump()

def generate_all_queries(schemas: List[Dict], api_key: str) -> List[Dict]:
    """Generate all possible query combinations for the given schemas."""
    lm_service, _ = init_services(api_key)
    
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
    
    for schema in schemas:
        for search, filter_, agg, group in itertools.product(
            search_options, filter_options, aggregation_options, groupby_options
        ):
            if not any([search, filter_, agg, group]):
                continue
                
            query = generate_single_query(schema, search, filter_, agg, group, lm_service)
            results.append({
                "database_schema": schema,
                "query": query
            })
            
    return results

if __name__ == "__main__":
    # This code only runs if the script is executed directly
    with open("../../data/3-collection-schemas-with-search-property.json", "r") as json_file:
        database_schemas = json.load(json_file)
    
    api_key = os.getenv("OPENAI_API_KEY")
    results = generate_all_queries(database_schemas, api_key)
    
    # Save results
    with open("synthetic-weaviate-queries-with-schemas.json", "w") as file:
        json.dump(results, file, indent=4)