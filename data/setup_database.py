import weaviate
import json
import pandas as pd
import os

# Connect to Weaviate Cloud
WEAVIATE_URL = ""
WEAVIATE_API_KEY = ""
OPENAI_API_KEY = ""
# Connect to Weaviate Cloud
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
    headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
)

def reset_database():
    """Clear all existing collections"""
    client.collections.delete_all()
    print("Database reset completed")

def create_schema(class_name, description, properties):
    """Create a single schema in Weaviate using the client API"""
    # Import the DataType enum
    from weaviate.collections.classes.config import DataType
    
    # Map Python/JSON types to Weaviate DataType enum values
    type_mapping = {
        "string": DataType.TEXT,
        "number": DataType.NUMBER,
        "boolean": DataType.BOOL,
        "text": DataType.TEXT
    }
    
    # Convert properties to Weaviate format
    weaviate_properties = []
    for prop in properties:
        data_type = type_mapping.get(prop['dataType'], DataType.TEXT)
        weaviate_properties.append({
            'name': prop['name'],
            'description': prop['description'],
            'data_type': data_type  # Pass the enum directly, not as a list
        })
    
    try:
        # Create the collection with the correct parameter structure
        collection = client.collections.create(
            name=class_name,
            description=description,
            properties=weaviate_properties,
            vectorizer_config=weaviate.classes.config.Configure.Vectorizer.text2vec_openai()
        )
        print(f"Created collection: {class_name}")
        return collection
    except Exception as e:
        print(f"Error creating collection {class_name}: {str(e)}")
        return None

def populate_data(collection_name, csv_path):
    """Populate a collection with data from a CSV file"""
    try:
        print(f"\n--- Starting data population for {collection_name} ---")
        print(f"Reading CSV from: {csv_path}")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        print(f"CSV loaded successfully with {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns: {', '.join(df.columns.tolist())}")
        
        # Get collection
        collection = client.collections.get(collection_name)
        print(f"Connected to collection: {collection_name}")
        
        # Get collection properties to check data types
        config = collection.config.get()
        properties_info = config.properties
        print(f"Collection properties: {[prop.name for prop in properties_info]}")
        
        property_types = {prop.name: prop.data_type.value for prop in properties_info}
        print(f"Property types: {property_types}")
        
        # Convert DataFrame to records
        records = df.to_dict('records')
        print(f"Converted {len(records)} records from DataFrame")
        
        # Show sample record for debugging
        if records:
            print(f"Sample record (before processing): {records[0]}")
        
        processed_records = []
        
        # Process each record for proper data typing
        for i, record in enumerate(records):
            if i < 3 or i % 100 == 0:  # Print first few and then every 100th for progress tracking
                print(f"Processing record {i+1}/{len(records)}")
                
            processed_record = {}
            for key, value in record.items():
                # Skip null/NaN values
                if pd.isna(value):
                    continue
                
                # Type conversion based on property type
                if key in property_types:
                    data_type = property_types[key]
                    if data_type == 'int' and not isinstance(value, int):
                        try:
                            processed_record[key] = int(value)
                        except (ValueError, TypeError):
                            print(f"Warning: Could not convert '{value}' to int for {key}")
                    elif data_type == 'number' and not isinstance(value, (int, float)):
                        try:
                            processed_record[key] = float(value)
                        except (ValueError, TypeError):
                            print(f"Warning: Could not convert '{value}' to float for {key}")
                    elif data_type == 'boolean' and not isinstance(value, bool):
                        if str(value).lower() in ('true', 't', 'yes', 'y', '1'):
                            processed_record[key] = True
                        elif str(value).lower() in ('false', 'f', 'no', 'n', '0'):
                            processed_record[key] = False
                        else:
                            print(f"Warning: Could not convert '{value}' to boolean for {key}")
                    else:
                        processed_record[key] = value
                else:
                    # Key not in schema properties
                    print(f"Warning: Column '{key}' not found in schema properties, skipping")
            
            processed_records.append(processed_record)
        
        # Show sample processed record for debugging
        if processed_records:
            print(f"Sample record (after processing): {processed_records[0]}")
        
        # Insert processed records in batches
        batch_size = 50
        success_count = 0
        error_count = 0
        
        for i in range(0, len(processed_records), batch_size):
            batch = processed_records[i:i+batch_size]
            print(f"Inserting batch {i//batch_size + 1}/{(len(processed_records) + batch_size - 1)//batch_size}")
            
            for record in batch:
                try:
                    # Print the exact record being inserted
                    print(f"Inserting: {record}")
                    collection.data.insert(properties=record)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Error inserting record: {record}")
                    print(f"Error details: {str(e)}")
            
            print(f"Batch progress: {success_count} successful, {error_count} failed")
        
        print(f"\nPopulation summary for {collection_name}:")
        print(f"Added {success_count} of {len(processed_records)} records")
        print(f"Failed: {error_count} records")
        
    except Exception as e:
        print(f"Error populating data for {collection_name}: {str(e)}")
        import traceback
        traceback.print_exc()

def process_schemas_file(schemas_file_path, csv_dir=None):
    """Process schemas file to create schemas and optionally populate with data"""
    # Reset database
    reset_database()
    
    # Load schemas
    with open(schemas_file_path, 'r') as f:
        schemas_json = json.load(f)
    
    print(f"Loaded {len(schemas_json)} schema definitions from {schemas_file_path}")
    
    # Track processed schemas
    processed_schemas = set()
    
    # Process each schema
    for schema_str in schemas_json:
        # Parse the schema JSON string
        schema_data = json.loads(schema_str)
        
        # Process each collection in the schema
        for collection in schema_data['weaviate_collections']:
            collection_name = collection['name']
            
            # Skip if already processed
            if collection_name in processed_schemas:
                continue
            
            print(f"\nProcessing collection: {collection_name}")
            
            # Prepare properties
            properties = [
                {
                    'name': prop['name'],
                    'description': prop['description'],
                    'dataType': prop['data_type'][0].lower()  # Convert to lowercase
                }
                for prop in collection['properties']
            ]
            
            print(f"Collection has {len(properties)} properties")
            
            # Create schema
            created_collection = create_schema(
                class_name=collection_name,
                description=collection['envisioned_use_case_overview'],
                properties=properties
            )
            
            # Only proceed if collection was created successfully and csv_dir is provided
            if created_collection is not None and csv_dir is not None:
                csv_path = os.path.join(csv_dir, f"{collection_name}.csv")
                if os.path.exists(csv_path):
                    print(f"Found CSV file: {csv_path}")
                    populate_data(collection_name, csv_path)
                else:
                    print(f"No CSV file found for {collection_name} at {csv_path}")
            
            processed_schemas.add(collection_name)
    
    print(f"\nProcessed {len(processed_schemas)} unique schemas")
    return list(processed_schemas)

def main():
    # Define paths
    schemas_file_path = "./3-collection-schemas-with-search-property.json"
    csv_data_dir = "./data-for-use-cases"
    
    print(f"Starting database setup with:")
    print(f"- Schemas file: {schemas_file_path}")
    print(f"- CSV directory: {csv_data_dir}")
    
    try:
        # Process schemas file and populate database
        processed_schemas = process_schemas_file(
            schemas_file_path=schemas_file_path,
            csv_dir=csv_data_dir
        )
        
        print("\nDatabase setup completed successfully!")
        print(f"Created and populated the following collections:")
        for schema in processed_schemas:
            print(f"- {schema}")
            
    except Exception as e:
        print(f"\nError during database setup: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close Weaviate client connection
        client.close()

if __name__ == "__main__":
    main()