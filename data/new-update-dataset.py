import json
import os

INPUT_FILE = "./updated-queries-with-schemas.json"
OUTPUT_FILE = "./weaviate-gorilla.json"

def generate_schema_description(collections):
    """
    Generate a general description of the database schema based on the collections.
    
    Args:
        collections: List of collection objects with their properties
        
    Returns:
        A string with a generalized description of the schema
    """
    description_parts = []
    
    for collection in collections:
        collection_name = collection.get("name", "Unknown")
        properties_text = []
        
        for prop in collection.get("properties", []):
            prop_name = prop.get("name", "Unknown")
            data_type = ", ".join(prop.get("data_type", ["Unknown"]))
            prop_desc = prop.get("description", "No description")
            
            properties_text.append(f"- {prop_name} ({data_type}): {prop_desc}")
        
        use_case = collection.get("envisioned_use_case_overview", "No use case description")
        
        collection_desc = f"Collection '{collection_name}':\n"
        collection_desc += "Properties:\n" + "\n".join(properties_text) + "\n"
        collection_desc += f"Use Case: {use_case}\n"
        
        description_parts.append(collection_desc)
    
    return "\n".join(description_parts)

def transform_record(record):
    """
    Transform a record by:
    1. Moving 'corresponding_natural_language_query' out of 'query' and renaming it
    2. Renaming 'query' to 'ground_truth_query'
    3. Renaming 'is_valid' to 'is_valid_lm_verifier'
    4. Renaming 'verification_rationale' to 'lm_verifier_rationale'
    5. Extracting 'weaviate_collections' from 'database_schema' and rename to 'weaviate_schemas'
    6. Creating a generalized schema description as 'generalized_schema_description'
    """
    transformed = {}
    
    # Copy all fields that are not being modified
    for key, value in record.items():
        if key not in ['database_schema', 'query', 'is_valid', 'verification_rationale']:
            transformed[key] = value
    
    # Extract and process database_schema
    if 'database_schema' in record:
        try:
            # Parse the JSON string into a Python object
            schema_data = json.loads(record['database_schema'])
            
            # Extract the weaviate_collections and rename to weaviate_schemas
            if 'weaviate_collections' in schema_data:
                transformed['weaviate_schemas'] = schema_data['weaviate_collections']
                
                # Generate generalized schema description
                transformed['generalized_schema_description'] = generate_schema_description(
                    schema_data['weaviate_collections']
                )
        except (json.JSONDecodeError, TypeError):
            # If there's an issue parsing the schema, keep the original
            transformed['database_schema'] = record['database_schema']
            print(f"Warning: Could not parse database_schema in a record. Keeping original.")
    
    # Handle the query restructuring
    if 'query' in record and isinstance(record['query'], dict):
        # Extract and rename corresponding_natural_language_query
        if 'corresponding_natural_language_query' in record['query']:
            transformed['natural_language_command'] = record['query']['corresponding_natural_language_query']
            
            # Create a copy of the query without the extracted field
            ground_truth_query = record['query'].copy()
            ground_truth_query.pop('corresponding_natural_language_query', None)
            transformed['ground_truth_query'] = ground_truth_query
        else:
            # If field doesn't exist, just rename the query
            transformed['ground_truth_query'] = record['query']
    
    # Rename is_valid to is_valid_lm_verifier
    if 'is_valid' in record:
        transformed['is_valid_lm_verifier'] = record['is_valid']
    
    # Rename verification_rationale to lm_verifier_rationale
    if 'verification_rationale' in record:
        transformed['lm_verifier_rationale'] = record['verification_rationale']
    
    return transformed

def main():
    # Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found.")
        return
    
    try:
        # Load the original file
        with open(INPUT_FILE, "r") as infile:
            data = json.load(infile)
        
        # Transform each record
        transformed_data = []
        if isinstance(data, list):
            transformed_data = [transform_record(record) for record in data]
            print(f"Transformed {len(transformed_data)} records.")
        else:
            # In case the input is a single JSON object
            transformed_data = transform_record(data)
            print("Transformed a single record.")
        
        # Write out the updated data to a new file
        with open(OUTPUT_FILE, "w") as outfile:
            json.dump(transformed_data, outfile, indent=4)
        
        print(f"Transformation complete! Updated data written to '{OUTPUT_FILE}'")
        
    except json.JSONDecodeError:
        print(f"Error: '{INPUT_FILE}' contains invalid JSON.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()