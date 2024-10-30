from models import SyntheticQuery
from create import CreateObjects

# load schemas from JSON
import json
with open("simple-synthetic-schemas.json", "r") as json_file:
    database_schemas = json.load(json_file)

search_apis = [
    "Semantic saerch through a collection"
]

filter_apis = [
    "Filter by an integer-valued property",
    "Filter by a text-valued property",
    "Filter by a boolean-valued property"
]

aggregate_apis = [
    "Aggregate a integer-valued property",
    "Aggregate a text-valued property",
    "Aggregate a boolean-valued property",
    "Count objects"
]

synthetic_queries = CreateObjects(
    
)

create_single_hop_query_prompt = f"""
Given a user's database schema and an API reference, write a natural language command simulating a case when the user would want to use the API.

[[ database schema ]]
{database_schema}

[[ API reference ]]
{api_reference}

[[ natural language command ]]
"""

# nested in a `for database_schema in database_schemas:`
# nested in a `for idx, API in enumerate(APIs)`:
# -- generate synthetic single-hop query with `create_objects(num_samples=1, create_single_hop_query_prompt, SyntheticQuery)`
# nested in another `for jdx, API in enumerate(APIs):`
# -- -- generate syntheic two-hop query with `create_objects(num_samples=1, create_two_hop_query_prompt, SyntheticQuery)`