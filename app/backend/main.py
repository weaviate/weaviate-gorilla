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

with open("synthetic-weaviate-queries-with-schemas.json", 'r') as f:
    synthetic_query_data = json.load(f)

print(synthetic_query_data[0]["query"]["corresponding_natural_language_query"])

# Example of the first row:
'''
{
    "database_schema": "{\"weaviate_collections\":[{\"name\":\"Restaurants\",\"properties\":[{\"name\":\"name\",\"data_type\":[\"string\"],\"description\":\"The name of the restaurant.\"},{\"name\":\"description\",\"data_type\":[\"string\"],\"description\":\"A detailed description and summary of the restaurant, including cuisine type and ambiance.\"},{\"name\":\"averageRating\",\"data_type\":[\"number\"],\"description\":\"The average rating score out of 5 for the restaurant.\"},{\"name\":\"openNow\",\"data_type\":[\"boolean\"],\"description\":\"A flag indicating whether the restaurant is currently open.\"}],\"envisioned_use_case_overview\":\"This schema focuses on enabling users to discover restaurants based on a comprehensive profile. With semantic search, users can find restaurants by cuisine, ambiance, or special features.\"},{\"name\":\"Menus\",\"properties\":[{\"name\":\"menuItem\",\"data_type\":[\"string\"],\"description\":\"The name of the menu item.\"},{\"name\":\"itemDescription\",\"data_type\":[\"string\"],\"description\":\"A detailed description of the menu item, including ingredients and preparation style.\"},{\"name\":\"price\",\"data_type\":[\"number\"],\"description\":\"The price of the menu item.\"},{\"name\":\"isVegetarian\",\"data_type\":[\"boolean\"],\"description\":\"A flag to indicate if the menu item is vegetarian.\"}],\"envisioned_use_case_overview\":\"This schema assists in linking dining experiences with specific restaurants through their menus. Rich search features allow customers to find dishes tailored to dietary needs and price points.\"},{\"name\":\"Reservations\",\"properties\":[{\"name\":\"reservationName\",\"data_type\":[\"string\"],\"description\":\"The name under which the reservation is made.\"},{\"name\":\"notes\",\"data_type\":[\"string\"],\"description\":\"Detailed notes about the reservation, such as special requests or celebrations.\"},{\"name\":\"partySize\",\"data_type\":[\"number\"],\"description\":\"The number of persons in the reservation.\"},{\"name\":\"confirmed\",\"data_type\":[\"boolean\"],\"description\":\"A flag indicating whether the reservation is confirmed.\"}],\"envisioned_use_case_overview\":\"This schema integrates with the restaurants by managing booking experiences. Semantic search of reservations can uncover trends in dining preferences and commonly requested meal attributes.\"}]}",
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
    }
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
    try:
        if 0 <= query_update.index < len(synthetic_query_data):
            synthetic_query_data[query_update.index]["query"] = query_update.updated_query
            return {"message": "Query updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Query index not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))