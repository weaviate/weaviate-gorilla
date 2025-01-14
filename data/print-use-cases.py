import json

# Read the JSON file
with open("./3-collection-schemas-with-search-property.json", "r") as f:
    schemas = json.load(f)

# Iterate through each schema
for i, schema_str in enumerate(schemas, 1):
    print(f"\n{'='*80}")
    print(f"Schema {i}:")
    print('='*80)
    
    # Parse the schema string into a dict
    schema = json.loads(schema_str)
    
    # Print each collection
    for collection in schema["weaviate_collections"]:
        print("\n\033[92mNEW USE CASE\033[0m")
        print(f"\nCollection: {collection['name']}")
        print(f"Use Case: {collection['envisioned_use_case_overview']}")
        print("\nProperties:")
        
        # Print each property
        for prop in collection['properties']:
            print(f"  - {prop['name']} ({', '.join(prop['data_type'])})")
            print(f"    {prop['description']}")
        
        print('-'*40)
