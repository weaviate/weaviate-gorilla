import weaviate
import weaviate.classes as wvc
import json
import pandas as pd
import os
from src.models import WeaviateQuery
from src.lm.query_executor import execute_weaviate_query

# Get API keys from environment variables
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("Connecting to Weaviate...")
weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
    headers = {
        "X-OpenAI-Api-Key": OPENAI_API_KEY
    }
)
print("Successfully connected to Weaviate...")

# Load queries from JSON file
with open('../../data/synthetic-weaviate-queries-with-schemas.json') as f:
    queries = json.load(f)

# Track created collections to avoid duplicates
created_collections = set()

# Process each query entry
for query_entry in queries:
    schema = json.loads(query_entry['database_schema'])
    
    # Create collections based on schema
    for collection in schema['weaviate_collections']:
        collection_name = collection['name']
        
        # Skip if collection already created
        if collection_name in created_collections:
            continue
            
        # Delete if exists
        if weaviate_client.collections.exists(collection_name):
            weaviate_client.collections.delete(collection_name)
            
        properties = []
        for prop in collection['properties']:
            data_type = wvc.config.DataType.TEXT
            if prop['data_type'][0] == 'number':
                data_type = wvc.config.DataType.NUMBER
            elif prop['data_type'][0] == 'boolean':
                data_type = wvc.config.DataType.BOOL
                
            properties.append(
                wvc.config.Property(
                    name=prop['name'],
                    data_type=data_type,
                    description=prop['description']
                )
            )
        
        weaviate_client.collections.create(
            name=collection_name,
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
            properties=properties,
            description=collection['envisioned_use_case_overview']
        )
        
        # Load and insert data from corresponding CSV
        csv_path = f'./{collection_name}.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            collection_obj = weaviate_client.collections.get(collection_name)
            for _, row in df.iterrows():
                collection_obj.data.insert(properties=row.to_dict())
                
        created_collections.add(collection_name)

print("Successfully created schema and populated collections with data")

# Execute all queries and store results
print("\nExecuting queries and storing results...")
for query_data in queries:
    print("\nQuery:", query_data['query']['corresponding_natural_language_query'])
    query = WeaviateQuery(**query_data['query'])
    try:
        result = execute_weaviate_query(weaviate_client, query)
        query_data['ground_truth_query_result'] = result
        print("\033[92mQuery executed successfully\033[0m")  # Green text
    except Exception as e:
        print(f"\033[91mQuery execution failed: {str(e)}\033[0m")  # Red text
        query_data['ground_truth_query_result'] = "QUERY EXECUTION FAILED"
        print("Connecting to Weaviate...")
        weaviate_client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_URL,
            auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
            headers={
                "X-OpenAI-Api-Key": OPENAI_API_KEY
            }
        )
        print("Successfully re-connected to Weaviate...")

# Save updated queries to new file
output_path = '../../data/synthetic-weaviate-queries-with-results.json'
with open(output_path, 'w') as f:
    json.dump(queries, f, indent=4)

print(f"\nResults saved to {output_path}")

# Close the Weaviate client connection
weaviate_client.close()
