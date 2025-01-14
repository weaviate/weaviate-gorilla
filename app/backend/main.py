# uvicorn main:app --reload

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

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

QUERIES_FILE = "synthetic-weaviate-queries-with-results.json"

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
    updated_result: str

@app.put("/update-query")
async def update_query(query_update: QueryUpdate):
    try:
        if 0 <= query_update.index < len(synthetic_query_data):
            synthetic_query_data[query_update.index]["query"] = query_update.updated_query
            synthetic_query_data[query_update.index]["ground_truth_query_result"] = query_update.updated_result
            
            with open(QUERIES_FILE, 'w') as f:
                json.dump(synthetic_query_data, f, indent=2)
                
            return {"message": "Query and result updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Query index not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))