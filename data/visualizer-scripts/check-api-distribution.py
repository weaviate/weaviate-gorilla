import json

with open("../synthetic-weaviate-queries.json", "r") as f:
    data = json.load(f)

print(data[0])

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

print(counts)
