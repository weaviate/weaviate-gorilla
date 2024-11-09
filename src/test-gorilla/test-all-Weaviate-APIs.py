from src.models import WeaviateQuery
from src.models import (
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation,
    GroupBy
)
from src.models import Tool, Function, Parameters, ParameterProperty
from src.utils.weaviate_fc_utils import get_collections_info
from src.lm.lm import LMService
from pydantic import BaseModel
from typing import Optional, Any
import json

def pretty_print_weaviate_query(query: WeaviateQuery) -> None:
    """Pretty prints a WeaviateQuery object with color and indentation."""
    print("\n\033[92mWeaviate Query Details:\033[0m")
    print(f"  \033[92mTarget Collection:\033[0m {query.target_collection}")
    print(f"  \033[92mSearch Query:\033[0m {query.search_query}")
    
    if query.integer_property_filter:
        print("  \033[92mInteger Filter:\033[0m")
        print(f"    Property: {query.integer_property_filter.property_name}")
        print(f"    Operator: {query.integer_property_filter.operator}")
        print(f"    Value: {query.integer_property_filter.value}")
    
    if query.text_property_filter:
        print("  \033[92mText Filter:\033[0m")
        print(f"    Property: {query.text_property_filter.property_name}")
        print(f"    Operator: {query.text_property_filter.operator}")
        print(f"    Value: {query.text_property_filter.value}")
        
    if query.boolean_property_filter:
        print("  \033[92mBoolean Filter:\033[0m")
        print(f"    Property: {query.boolean_property_filter.property_name}")
        print(f"    Operator: {query.boolean_property_filter.operator}")
        print(f"    Value: {query.boolean_property_filter.value}")
        
    if query.integer_property_aggregation:
        print("  \033[92mInteger Aggregation:\033[0m")
        print(f"    Property: {query.integer_property_aggregation.property_name}")
        print(f"    Metrics: {query.integer_property_aggregation.metrics}")
        
    if query.text_property_aggregation:
        print("  \033[92mText Aggregation:\033[0m")
        print(f"    Property: {query.text_property_aggregation.property_name}")
        print(f"    Metrics: {query.text_property_aggregation.metrics}")
        
    if query.boolean_property_aggregation:
        print("  \033[92mBoolean Aggregation:\033[0m")
        print(f"    Property: {query.boolean_property_aggregation.property_name}")
        print(f"    Metrics: {query.boolean_property_aggregation.metrics}")
        
    if query.groupby_property:
        print(f"  \033[92mGroup By:\033[0m {query.groupby_property}")
        
    print(f"  \033[92mNatural Language Query:\033[0m {query.corresponding_natural_language_query}")

with open("../../data/synthetic-weaviate-queries.json", "r") as json_file:
    weaviate_queries_raw = json.load(json_file)
    weaviate_queries = []
    
    for query in weaviate_queries_raw:
        # Create filter objects if they exist
        int_filter = IntPropertyFilter(**query["integer_property_filter"]) if query["integer_property_filter"] else None
        text_filter = TextPropertyFilter(**query["text_property_filter"]) if query["text_property_filter"] else None
        bool_filter = BooleanPropertyFilter(**query["boolean_property_filter"]) if query["boolean_property_filter"] else None
        
        # Create aggregation objects if they exist
        int_agg = IntAggregation(**query["integer_property_aggregation"]) if query["integer_property_aggregation"] else None
        text_agg = TextAggregation(**query["text_property_aggregation"]) if query["text_property_aggregation"] else None
        bool_agg = BooleanAggregation(**query["boolean_property_aggregation"]) if query["boolean_property_aggregation"] else None

        # Create WeaviateQuery object
        weaviate_query = WeaviateQuery(
            target_collection=query["target_collection"],
            search_query=query["search_query"],
            integer_property_filter=int_filter,
            text_property_filter=text_filter,
            boolean_property_filter=bool_filter,
            integer_property_aggregation=int_agg,
            text_property_aggregation=text_agg,
            boolean_property_aggregation=bool_agg,
            groupby_property=query["groupby_property"],
            corresponding_natural_language_query=query["corresponding_natural_language_query"]
        )
        weaviate_queries.append(weaviate_query)

pretty_print_weaviate_query(weaviate_queries[0])