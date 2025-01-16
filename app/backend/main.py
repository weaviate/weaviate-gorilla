from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from src.lm.query_executor import execute_weaviate_query
from src.lm.lm import LMService
from src.models import (
    WeaviateQuery,
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation
)
import json
import os
import weaviate

from src.generate_queries.generate_queries import (
    search_query_desc,
    text_property_filter_desc,
    int_property_filter_desc,
    boolean_property_filter_desc,
    text_property_aggregation_desc,
    int_property_aggregation_desc,
    boolean_property_aggregation_desc,
    groupby_desc,
    generate_single_query,
    init_services,
    generate_single_query,
    get_query_prompt
)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUERIES_FILE = "synthetic-weaviate-queries-with-results.json"
SCHEMAS_FILE = "3-collection-schemas-with-search-property.json"

# Get API keys from environment variables
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("Connecting to Weaviate...")
weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
    headers = {
        "X-OpenAI-Api-Key": OPENAI_API_KEY
    }
)
print("Successfully connected to Weaviate...")

# Load schemas data into memory at startup
with open(SCHEMAS_FILE, 'r') as f:
    schemas_data = json.load(f)

lm_service, _ = init_services(OPENAI_API_KEY)

with open(QUERIES_FILE, 'r') as f:
    synthetic_query_data = json.load(f)

@app.get("/data")
async def get_data():
    return synthetic_query_data

class QueryUpdate(BaseModel):
    index: int
    updated_query: Dict[Any, Any]

@app.put("/update-query")
async def update_query(query_update: QueryUpdate):
    print(query_update)
    try:
        # 1) Validate the requested index
        if not (0 <= query_update.index < len(synthetic_query_data)):
            raise HTTPException(status_code=404, detail="Query index not found")
        
        # 2) Overwrite the existing "query" field with the updated query data
        synthetic_query_data[query_update.index]["query"] = query_update.updated_query
        
        # 3) Build a WeaviateQuery object from the updated query dictionary
        updated_query_obj = WeaviateQuery(**query_update.updated_query)

        # 4) Execute the query to get the new ground-truth result
        final_response = execute_weaviate_query(weaviate_client, updated_query_obj)
        
        # 5) Update ground_truth_query_result and save changes to disk
        synthetic_query_data[query_update.index]["ground_truth_query_result"] = final_response

        with open(QUERIES_FILE, 'w') as f:
            json.dump(synthetic_query_data, f, indent=2)
        
        return {"message": "Query and ground truth result updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

OPERATOR_DESCRIPTIONS = {
    "search_query": search_query_desc,
    "text_property_filter": text_property_filter_desc,
    "integer_property_filter": int_property_filter_desc,
    "boolean_property_filter": boolean_property_filter_desc,
    "text_property_aggregation": text_property_aggregation_desc,
    "integer_property_aggregation": int_property_aggregation_desc,
    "boolean_property_aggregation": boolean_property_aggregation_desc,
    "groupby_property": groupby_desc
}

class QueryConfig(BaseModel):
    target_collection: str
    search_query: Optional[bool] = False
    integer_property_filter: Optional[Dict] = None
    text_property_filter: Optional[Dict] = None
    boolean_property_filter: Optional[Dict] = None
    integer_property_aggregation: Optional[Dict] = None
    text_property_aggregation: Optional[Dict] = None
    boolean_property_aggregation: Optional[Dict] = None
    groupby_property: Optional[str] = None

def map_config_to_operators(query_config: QueryConfig):
    """Map the query config to operator tuples used by generate_single_query."""
    operators = {
        'search': None,
        'filter': None,
        'agg': None,
        'group': None
    }
    
    # Map search query
    if query_config.search_query:
        operators['search'] = ("search_query", str)
    
    # Map filters
    if query_config.integer_property_filter:
        operators['filter'] = ("integer_property_filter", "IntPropertyFilter")
    elif query_config.text_property_filter:
        operators['filter'] = ("text_property_filter", "TextPropertyFilter")
    elif query_config.boolean_property_filter:
        operators['filter'] = ("boolean_property_filter", "BooleanPropertyFilter")
        
    # Map aggregations
    if query_config.integer_property_aggregation:
        operators['agg'] = ("integer_property_aggregation", "IntAggregation")
    elif query_config.text_property_aggregation:
        operators['agg'] = ("text_property_aggregation", "TextAggregation")
    elif query_config.boolean_property_aggregation:
        operators['agg'] = ("boolean_property_aggregation", "BooleanAggregation")
        
    # Map groupby
    if query_config.groupby_property:
        operators['group'] = ("groupby_property", str)
        
    return operators

@app.post("/generate-nl-query")
async def generate_natural_language_query(query_config: QueryConfig):
    try:
        print(f"Received query config for collection: {query_config.target_collection}")
        print(f"Search query enabled: {query_config.search_query}")
        print(f"Integer filter config: {query_config.integer_property_filter}")
        print(f"Text filter config: {query_config.text_property_filter}")
        print(f"Boolean filter config: {query_config.boolean_property_filter}")
        print(f"Integer aggregation config: {query_config.integer_property_aggregation}")
        print(f"Text aggregation config: {query_config.text_property_aggregation}")
        print(f"Boolean aggregation config: {query_config.boolean_property_aggregation}")
        print(f"Groupby property: {query_config.groupby_property}")

        # Map the config to operators
        operators = map_config_to_operators(query_config)
        print(f"Mapped operators: {operators}")
        
        # Create a minimal schema for the query
        schema = {
            "weaviate_collections": [{
                "name": query_config.target_collection,
                "properties": []
            }]
        }
        
        # Generate query using the generate_queries.py functionality
        query_result = generate_single_query(
            schema=schema,
            search=operators['search'],
            filter_=operators['filter'],
            agg=operators['agg'],
            group=operators['group'],
            lm_service=lm_service
        )
        
        print(f"Generated natural language query: {query_result['corresponding_natural_language_query']}")
        return {"natural_language_query": query_result["corresponding_natural_language_query"]}
        
    except Exception as e:
        print(f"Error generating query: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/collection-properties")
async def get_collection_properties(collection_name: str):
    try:
        # Search through all schema groups using the in-memory schemas_data
        for schema_group in schemas_data:
            schema_obj = json.loads(schema_group)
            for collection in schema_obj["weaviate_collections"]:
                if collection["name"] == collection_name:
                    # Return the properties for the matching collection
                    return {
                        "properties": [
                            {
                                "name": prop["name"],
                                "data_type": prop["data_type"][0]  # Taking first type since it's an array
                            }
                            for prop in collection["properties"]
                        ]
                    }
                    
        # If collection not found, raise 404
        raise HTTPException(status_code=404, detail=f"Collection {collection_name} not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))