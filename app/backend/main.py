# uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

with open("llama3.1:8b-experiment_results-with-models.json", 'r') as f:
    sample_data = json.load(f)

print(sample_data["detailed_results"][0])

'''
Example of the first row:

{'query_index': 0, 'database_schema_index': 0, 'natural_language_query': 'Find average and maximum prices of vegetarian dishes that mention "spicy" in their name or description and group the results by dish category.', 'ground_truth_query': {'database_schema': {'weaviate_collections': [{'name': 'RestaurantMenu', 'properties': [{'name': 'DishName', 'data_type': ['string'], 'description': 'The name of the dish offered in the restaurant menu.'}, {'name': 'Price', 'data_type': ['number'], 'description': 'The price of the dish.'}, {'name': 'IsVegetarian', 'data_type': ['boolean'], 'description': 'Indicates if the dish is vegetarian.'}], 'envisioned_use_case_overview': 'The RestaurantMenu collection stores details about each dish offered in a restaurant, including their names, prices, and vegetarian status. This information allows for menu management and facilitates the creation of customer-friendly menu displays.'}, {'name': 'CustomerOrders', 'properties': [{'name': 'CustomerName', 'data_type': ['string'], 'description': 'The name of the customer who places the order.'}, {'name': 'TotalAmount', 'data_type': ['number'], 'description': "The total amount for the customer's order."}, {'name': 'IsTakeaway', 'data_type': ['boolean'], 'description': 'Indicates whether the order is for takeaway or dine-in.'}], 'envisioned_use_case_overview': 'The CustomerOrders collection captures details of customer orders, including their names, total amounts, and whether the orders are takeaway. This collection helps in processing orders and managing order histories.'}, {'name': 'StaffMembers', 'properties': [{'name': 'StaffName', 'data_type': ['string'], 'description': 'The name of the staff member.'}, {'name': 'ExperienceYears', 'data_type': ['number'], 'description': 'The number of years of experience the staff member has.'}, {'name': 'IsOnDuty', 'data_type': ['boolean'], 'description': 'Indicates if the staff member is currently on duty.'}], 'envisioned_use_case_overview': "The StaffMembers collection maintains information about the restaurant's staff, including their names, experience, and current duty status. This collection is essential for scheduling and managing staffing levels."}]}, 'corresponding_natural_language_query': 'Find average and maximum prices of vegetarian dishes that mention "spicy" in their name or description and group the results by dish category.', 'target_collection': 'RestaurantMenu', 'search_query': 'vegetarian spicy', 'integer_property_filter': {'property_name': 'isVegetarian', 'operator': '=', 'value': 1}, 'text_property_filter': None, 'boolean_property_filter': None, 'integer_property_aggregation': {'property_name': 'price', 'metrics': 'MIN'}, 'text_property_aggregation': None, 'boolean_property_aggregation': None, 'groupby_property': 'category'}, 'predicted_query': {'corresponding_natural_language_query': 'Find average and maximum prices of vegetarian dishes that mention "spicy" in their name or description and group the results by dish category.', 'target_collection': 'RestaurantMenu', 'search_query': None, 'integer_property_filter': None, 'text_property_filter': None, 'boolean_property_filter': None, 'integer_property_aggregation': None, 'text_property_aggregation': None, 'boolean_property_aggregation': None, 'groupby_property': None}, 'ast_score': 0.6000000000000001, 'error': None}
'''

@app.get("/data")
async def get_data():
    return sample_data["detailed_results"]