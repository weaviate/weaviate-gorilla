import weaviate
import json
import requests
import pandas as pd
import os

# Connect to Weaviate and populate datasets
client = weaviate.connect_to_local(
    headers={
        "X-OpenAI-Api-Key": ""
    }
)
WEAVIATE_URL = "http://localhost:8080/v1/schema"

def reset_database():
    """Clear all existing collections"""
    client.collections.delete_all()
    print("Database reset completed")

def create_schema(class_name, description, properties):
    """Create a single schema in Weaviate"""
    # Map Python/JSON types to Weaviate types
    type_mapping = {
        "string": "text",
        "number": "number",
        "boolean": "boolean",
        "text": "text"
    }
    
    # Convert properties to Weaviate format
    weaviate_properties = []
    for prop in properties:
        data_type = type_mapping.get(prop['dataType'], 'text')
        weaviate_properties.append({
            'name': prop['name'],
            'description': prop['description'],
            'dataType': [data_type]  # Weaviate expects an array of types
        })
    
    schema_dict = {
        'class': class_name,
        'description': description,
        'properties': weaviate_properties,
        'vectorizer': 'text2vec-openai'
    }
    
    response = requests.post(
        url=WEAVIATE_URL,
        data=json.dumps(schema_dict),
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        print(f"Created collection: {class_name}")
    else:
        print(f"Error creating collection {class_name}: {response.text}")

def populate_data(collection_name, csv_path):
    """Populate a collection with data from a CSV file"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Get collection
        collection = client.collections.get(collection_name)
        
        # Convert DataFrame to records
        records = df.to_dict('records')
        
        # Insert records one by one
        for record in records:
            collection.data.insert(properties=record)
        
        print(f"Added {len(records)} records to {collection_name}")
        
    except Exception as e:
        print(f"Error populating data for {collection_name}: {str(e)}")

def process_queries_file(queries_file_path, csv_dir=None):
    """Process queries file to create schemas and optionally populate with data"""
    # Reset database
    reset_database()
    
    # Load queries
    with open(queries_file_path, 'r') as f:
        queries = json.load(f)
    
    # Track processed schemas
    processed_schemas = set()
    
    # Process each query
    for query in queries:
        # Parse the database_schema JSON string
        schema_data = json.loads(query['database_schema'])
        
        # Process each collection in the schema
        for collection in schema_data['weaviate_collections']:
            collection_name = collection['name']
            
            # Skip if already processed
            if collection_name in processed_schemas:
                continue
            
            # Prepare properties
            properties = [
                {
                    'name': prop['name'],
                    'description': prop['description'],
                    'dataType': prop['data_type'][0].lower()  # Convert to lowercase
                }
                for prop in collection['properties']
            ]
            
            # Create schema
            create_schema(
                class_name=collection_name,
                description=collection['envisioned_use_case_overview'],
                properties=properties
            )
            
            # Populate data if CSV directory is provided
            if csv_dir:
                csv_path = os.path.join(csv_dir, f"{collection_name}.csv")
                if os.path.exists(csv_path):
                    populate_data(collection_name, csv_path)
                else:
                    print(f"No CSV file found for {collection_name}")
            
            processed_schemas.add(collection_name)
    
    print(f"\nProcessed {len(processed_schemas)} unique schemas")
    return list(processed_schemas)

def main():
    # Define paths
    queries_file_path = "../../data/synthetic-weaviate-queries-with-schemas.json"
    csv_data_dir = "../../data/data-for-use-cases"
    
    try:
        # Process queries file and populate database
        processed_schemas = process_queries_file(
            queries_file_path=queries_file_path,
            csv_dir=csv_data_dir
        )
        
        print("\nDatabase setup completed successfully!")
        print(f"Created and populated the following collections:")
        for schema in processed_schemas:
            print(f"- {schema}")
            
    except Exception as e:
        print(f"\nError during database setup: {str(e)}")
    finally:
        # Close Weaviate client connection
        client.close()

if __name__ == "__main__":
    main()