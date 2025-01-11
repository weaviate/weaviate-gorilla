import json
from typing import Optional
from pydantic import create_model, Field, BaseModel
from src.lm.lm import LMService
from src.vectorizer.vectorizer import VectorizerService

openai_api_key = ""

lm_service = LMService(
    model_provider = "openai", 
    model_name = "gpt-4o",
    api_key = openai_api_key
)

lm_service.connection_test()

vectorizer_service = VectorizerService(
    model_provider = "openai",
    model_name = "text-embedding-3-small", 
    api_key = openai_api_key
)

vectorizer_service.connection_test()

# Load the schema definitions
with open("../generate-schemas/3-collection-schemas-with-search-property.json", "r") as file:
    raw_schemas = json.load(file)
    # Parse the JSON strings into dictionaries
    schemas = [json.loads(schema_str) for schema_str in raw_schemas]

generate_data_prompt = """
Generate synthetic data for the following collection schema:

Collection Name: {collection_name}

Properties:
{properties}

Generate a single realistic data object that could exist in this collection. The data should be high quality and realistic.
Make sure text fields like descriptions are detailed and natural sounding (at least 2-3 sentences for descriptive fields).
Numeric fields should be realistic values within expected ranges.
Boolean fields should make logical sense for the record.

Format the response as a JSON object with all required properties. For example:
{{
    "property1": "value1",
    "property2": 123,
    "property3": true
}}

The response must be valid JSON and include ALL properties listed above.
"""

results = []
markdown_output = "# Generated Collection Data\n\n"

# Process each schema
for schema_idx, schema_set in enumerate(schemas, 1):
    collections_data = []
    markdown_output += f"## Schema Set {schema_idx}\n\n"
    
    # Process each collection in the schema
    for collection in schema_set["weaviate_collections"]:
        collection_name = collection["name"]
        properties = collection["properties"]
        
        markdown_output += f"### {collection_name}\n\n"
        markdown_output += "| Property | Value |\n|----------|--------|\n"
        
        # Create property definitions for dynamic model
        model_properties = {}
        for prop in properties:
            if prop["data_type"][0] == "string":  # Changed from "TEXT" to "string"
                model_properties[prop["name"]] = (str, Field(..., description=prop["description"]))
            elif prop["data_type"][0] == "number":  # Changed from "NUMBER" to "number"
                model_properties[prop["name"]] = (float, Field(..., description=prop["description"]))
            elif prop["data_type"][0] == "boolean":  # Changed from "BOOLEAN" to "boolean"
                model_properties[prop["name"]] = (bool, Field(..., description=prop["description"]))
                
        # Create dynamic model for this collection
        DynamicDataModel = create_model(
            f'{collection_name}Model',
            **model_properties
        )
        
        # Format properties for prompt
        properties_str = "\n".join([
            f"- {p['name']} ({p['data_type'][0]}): {p['description']}"
            for p in properties
        ])
        
        # Generate 10 records for this collection
        collection_records = []
        retries = 3
        for i in range(10):
            success = False
            for attempt in range(retries):
                try:
                    task_instructions = generate_data_prompt.format(
                        collection_name=collection_name,
                        properties=properties_str
                    )
                    
                    record = lm_service.generate(task_instructions, DynamicDataModel)
                    if record:
                        record_dict = record.model_dump()
                        collection_records.append(record_dict)
                        success = True
                        break
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for record {i} of {collection_name}: {str(e)}")
                    continue
                    
            if not success:
                print(f"Failed to generate valid record {i} for {collection_name} after {retries} attempts")
                continue
                
            # Add first record to markdown
            if i == 0:
                for key, value in record_dict.items():
                    markdown_output += f"| {key} | {value} |\n"
                markdown_output += "\n"
            
        collections_data.append({
            "collection_name": collection_name,
            "records": collection_records
        })
        
        print(f"\nGenerated {len(collection_records)} records for {collection_name}")
        if collection_records:
            print("Sample record:")
            print(json.dumps(collection_records[0], indent=2))
        
    results.append({
        "schema": schema_set,
        "collections_data": collections_data
    })

# Save JSON results
with open("synthetic-collection-data.json", "w") as file:
    json.dump(results, file, indent=4)

# Save markdown results
with open("synthetic-collection-data.md", "w") as file:
    file.write(markdown_output)
