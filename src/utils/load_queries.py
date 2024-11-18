from src.models import (
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation,
    WeaviateQueryWithSchema
)
import json

def load_queries(file_path: str):
    with open(file_path, "r") as json_file:
        weaviate_queries_raw = json.load(json_file)
        print(f"\033[92mLoaded {len(weaviate_queries_raw)} raw queries\033[0m")
        weaviate_queries = []
        database_schemas = []
        
        for query_idx, query_data in enumerate(weaviate_queries_raw):
            query = query_data["query"]
            database_schema = query_data["database_schema"]
            
            # Create filter objects if they exist
            int_filter = None
            if query["integer_property_filter"]:
                int_filter_data = query["integer_property_filter"].copy()
                if int_filter_data["property_name"]:  # Check if property_name exists and is not empty
                    int_filter_data["property_name"] = int_filter_data["property_name"][0].lower() + int_filter_data["property_name"][1:]
                int_filter = IntPropertyFilter(**int_filter_data)
                
            text_filter = None
            if query["text_property_filter"]:
                text_filter_data = query["text_property_filter"].copy()
                if text_filter_data["property_name"]:  # Check if property_name exists and is not empty
                    text_filter_data["property_name"] = text_filter_data["property_name"][0].lower() + text_filter_data["property_name"][1:]
                text_filter = TextPropertyFilter(**text_filter_data)
                
            bool_filter = None
            if query["boolean_property_filter"]:
                bool_filter_data = query["boolean_property_filter"].copy()
                if bool_filter_data["property_name"]:  # Check if property_name exists and is not empty
                    bool_filter_data["property_name"] = bool_filter_data["property_name"][0].lower() + bool_filter_data["property_name"][1:]
                bool_filter = BooleanPropertyFilter(**bool_filter_data)
            
            # Create aggregation objects if they exist
            int_agg = None
            if query["integer_property_aggregation"]:
                int_agg_data = query["integer_property_aggregation"].copy()
                if int_agg_data["property_name"]:  # Check if property_name exists and is not empty
                    int_agg_data["property_name"] = int_agg_data["property_name"][0].lower() + int_agg_data["property_name"][1:]
                int_agg = IntAggregation(**int_agg_data)
                
            text_agg = None
            if query["text_property_aggregation"]:
                text_agg_data = query["text_property_aggregation"].copy()
                if text_agg_data["property_name"]:  # Check if property_name exists and is not empty
                    text_agg_data["property_name"] = text_agg_data["property_name"][0].lower() + text_agg_data["property_name"][1:]
                text_agg = TextAggregation(**text_agg_data)
                
            bool_agg = None
            if query["boolean_property_aggregation"]:
                bool_agg_data = query["boolean_property_aggregation"].copy()
                if bool_agg_data["property_name"]:  # Check if property_name exists and is not empty
                    bool_agg_data["property_name"] = bool_agg_data["property_name"][0].lower() + bool_agg_data["property_name"][1:]
                bool_agg = BooleanAggregation(**bool_agg_data)

            # Create WeaviateQueryWithSchema object
            
            # Convert database_schema string to dict if needed
            if isinstance(database_schema, str):
                database_schema = json.loads(database_schema)
                
            weaviate_query = WeaviateQueryWithSchema(
                target_collection=query["target_collection"],
                search_query=query["search_query"],
                integer_property_filter=int_filter,
                text_property_filter=text_filter,
                boolean_property_filter=bool_filter,
                integer_property_aggregation=int_agg,
                text_property_aggregation=text_agg,
                boolean_property_aggregation=bool_agg,
                groupby_property=query["groupby_property"][0].lower() + query["groupby_property"][1:] if query["groupby_property"] else None,
                corresponding_natural_language_query=query["corresponding_natural_language_query"],
                database_schema=database_schema
            )
            weaviate_queries.append(weaviate_query)
        
        return weaviate_queries
