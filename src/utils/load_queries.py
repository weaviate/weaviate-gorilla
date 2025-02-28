from src.models import (
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation,
    WeaviateQueryWithSchema,
    WeaviateCollections,
    WeaviateCollectionConfig,
    Property
)
import json

def load_queries(file_path: str):
    with open(file_path, "r") as json_file:
        weaviate_queries_raw = json.load(json_file)
        print(f"\033[92mLoaded {len(weaviate_queries_raw)} raw queries\033[0m")
        weaviate_queries = []
        
        for query_data in weaviate_queries_raw:
            query = query_data["ground_truth_query"]
            database_schema_raw = query_data["weaviate_schemas"]
            
            # Create filter objects if they exist
            int_filter = None
            if query.get("integer_property_filter"):
                int_filter = IntPropertyFilter(**query["integer_property_filter"])
                
            text_filter = None
            if query.get("text_property_filter"):
                text_filter = TextPropertyFilter(**query["text_property_filter"])
                
            bool_filter = None
            if query.get("boolean_property_filter"):
                bool_filter = BooleanPropertyFilter(**query["boolean_property_filter"])
            
            # Create aggregation objects if they exist
            int_agg = None
            if query.get("integer_property_aggregation"):
                int_agg = IntAggregation(**query["integer_property_aggregation"])
                
            text_agg = None
            if query.get("text_property_aggregation"):
                text_agg = TextAggregation(**query["text_property_aggregation"])
                
            bool_agg = None
            if query.get("boolean_property_aggregation"):
                bool_agg = BooleanAggregation(**query["boolean_property_aggregation"])

            # Convert database_schema to WeaviateCollections
            if isinstance(database_schema_raw, str):
                database_schema_raw = json.loads(database_schema_raw)
            
            # Create WeaviateCollections from the schema data
            collections = []
            for collection_data in database_schema_raw:
                properties = []
                for prop in collection_data.get("properties", []):
                    properties.append(Property(
                        name=prop["name"],
                        data_type=prop["data_type"],
                        description=prop["description"]
                    ))
                
                collections.append(WeaviateCollectionConfig(
                    name=collection_data["name"],
                    properties=properties,
                    envisioned_use_case_overview=collection_data.get("envisioned_use_case_overview", "")
                ))
            
            database_schema = WeaviateCollections(weaviate_collections=collections)
                
            weaviate_query = WeaviateQueryWithSchema(
                target_collection=query["target_collection"],
                search_query=query.get("search_query"),
                integer_property_filter=int_filter,
                text_property_filter=text_filter,
                boolean_property_filter=bool_filter,
                integer_property_aggregation=int_agg,
                text_property_aggregation=text_agg,
                boolean_property_aggregation=bool_agg,
                groupby_property=query.get("groupby_property"),
                corresponding_natural_language_query=query_data["natural_language_command"],
                database_schema=database_schema
            )
            weaviate_queries.append(weaviate_query)
        
        return weaviate_queries
