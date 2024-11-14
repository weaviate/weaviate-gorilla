import json

with open("../new-synthetic-weaviate-queries-with-schemas.json", "r") as f:
    data = json.load(f)

print(json.dumps(data[0], indent=4))

# Define the properties we want to check
properties_to_check = [
    'search_query',
    'integer_property_filter', 
    'text_property_filter',
    'boolean_property_filter',
    'integer_property_aggregation',
    'text_property_aggregation',
    'boolean_property_aggregation',
    'groupby_property'
]

counts = {}

for prop in properties_to_check:
    counts[prop] = sum(d[prop] is not None for d in data)

print(json.dumps(counts, indent=4))

'''
{
    "search_query": 239,
    "integer_property_filter": 334,
    "text_property_filter": 104,
    "boolean_property_filter": 365,
    "integer_property_aggregation": 97,
    "text_property_aggregation": 35,
    "boolean_property_aggregation": 41,
    "groupby_property": 99
}
'''