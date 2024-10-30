import json

# Read the original file
with open("./data/simple-3-collection-schemas.json", "r") as file:
    data = json.load(file)

# Process each schema string
processed_data = []
for schema_str in data:
    # Parse the string into a dictionary
    schema_dict = json.loads(schema_str)
    
    # For each collection in the schema
    for collection in schema_dict["weaviate_collections"]:
        # Rename 'name' to 'class'
        collection["class"] = collection.pop("name")
        # Rename 'envisioned_use_case_overview' to 'description'
        collection["description"] = collection.pop("envisioned_use_case_overview")
        collection["vectorIndexType"] = "hnsw"
        collection["vectorizer"] = "text2vec-transformers"
        
    # Convert back to string
    processed_data.append(json.dumps(schema_dict))

# Write the processed data back to file
with open("./data/simple-3-collection-schemas.json", "w") as file:
    json.dump(processed_data, file, indent=4)
