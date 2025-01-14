# uvicorn main:app --reload

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.lm.query_executor import execute_weaviate_query
from src.models import WeaviateQuery

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import json
import os
import weaviate

QUERIES_FILE = "synthetic-weaviate-queries-with-results.json"

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

with open(QUERIES_FILE, 'r') as f:
    synthetic_query_data = json.load(f)

print(synthetic_query_data[0]["query"]["corresponding_natural_language_query"])

# Example of the first row:
'''
{
    "database_schema": "{\"weaviate_collections\":[{\"name\":\"Restaurants\",...}]}",
    "query": {
        "corresponding_natural_language_query": "What is the average price of seasonal specialty menu items under $20, grouped by whether they are vegetarian or not?",
        "target_collection": "Menus",
        "search_query": "seasonal specialties",
        "integer_property_filter": {
            "property_name": "price",
            "operator": "<",
            "value": 20
        },
        "text_property_filter": null,
        "boolean_property_filter": null,
        "integer_property_aggregation": {
            "property_name": "price",
            "metrics": "MEAN"
        },
        "text_property_aggregation": null,
        "boolean_property_aggregation": null,
        "groupby_property": "isVegetarian"
    },
    "ground_truth_query_result": "Grouped aggregation results:\n----------------------------------------\nGroup: isVegetarian = true\nProperty: price\n  mean: 15.5\nGroup count: 2\n----------------------------------------\nGroup: isVegetarian = false\nProperty: price\n  mean: 17.0\nGroup count: 1\n"
}
'''

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