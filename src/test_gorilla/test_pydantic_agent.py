import asyncio
import os
import json
from datetime import datetime
import pandas as pd
from typing import List, Dict, Optional

import weaviate
import weaviate.classes as wvc
from weaviate.classes.init import Auth

from src.lm.pydantic_agents.agent import WeaviateSearchAgentSimple
from src.models import ExperimentSummary

def parse_schema(schema_str: str) -> Dict:
    """Parse the database schema string into a dictionary."""
    try:
        return json.loads(schema_str)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse database schema: {e}")
        return {}

def load_collection_data(collection_name: str) -> List[Dict]:
    """Load data from CSV file for a collection."""
    csv_path = f"../../data/data-for-use-cases/{collection_name}.csv"
    print(f"\nLoading data from {csv_path}")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        print(f"Successfully read CSV with {len(df)} rows and {len(df.columns)} columns")
        print("Columns found:", ", ".join(df.columns))
        
        # Convert DataFrame to list of dictionaries with proper nesting
        data = []
        numeric_conversions = 0
        for idx, row in df.iterrows():
            # Convert any numeric strings to float if they represent numbers
            properties = {}
            for col in df.columns:
                val = row[col]
                if isinstance(val, str) and val.replace('.', '').isdigit():
                    properties[col] = float(val)
                    numeric_conversions += 1
                else:
                    properties[col] = val
            
            data.append({"properties": properties})
            
            # Log progress for large datasets
            if (idx + 1) % 1000 == 0:
                print(f"Processed {idx + 1} rows...")
        
        print(f"Loaded {len(data)} records for {collection_name}")
        print(f"Performed {numeric_conversions} numeric conversions")
        print("Sample record:", json.dumps(data[0], indent=2))
        return data
        
    except Exception as e:
        print(f"Error loading data for {collection_name}: {str(e)}")
        return []

async def setup_collections(client, schema_data: Dict):
    """Set up all collections defined in the schema."""
    collections = {}
    
    # Get collections from schema
    total_collections = len(schema_data.get('weaviate_collections', []))
    print(f"\nSetting up {total_collections} collections...")
    
    for idx, collection_def in enumerate(schema_data.get('weaviate_collections', []), 1):
        collection_name = collection_def['name']
        print(f"\n[{idx}/{total_collections}] Processing collection: {collection_name}")
        
        # Check if collection exists
        collection_exists = client.collections.exists(collection_name)
        if collection_exists:
            print(f"Collection {collection_name} already exists, skipping creation and data loading")
            collections[collection_name] = client.collections.get(collection_name)
            continue

        print(f"Creating {collection_name} collection with properties:")
        for prop in collection_def['properties']:
            print(f"- {prop['name']} ({prop['data_type'][0].upper()})")
            print(f"  Description: {prop.get('description', 'No description provided')}")
        
        # Map data types
        type_mapping = {
            'string': wvc.config.DataType.TEXT,
            'number': wvc.config.DataType.NUMBER,
            'boolean': wvc.config.DataType.BOOL,
            'bool': wvc.config.DataType.BOOL  # Add mapping for 'bool' type
        }
        
        # Create collection
        try:
            collection = await client.collections.create(
                name=collection_name,
                vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
                properties=[
                    wvc.config.Property(
                        name=prop['name'],
                        data_type=type_mapping[prop['data_type'][0].lower()],  # Convert to lowercase for case-insensitive matching
                        description=prop['description']
                    )
                    for prop in collection_def['properties']
                ]
            )
            collections[collection_name] = collection
            print(f"{collection_name} collection created successfully")
            
            # Load and insert data for this collection
            data = load_collection_data(collection_name)
            total_records = len(data)
            print(f"Inserting {total_records} records into {collection_name}")
            
            successful_inserts = 0
            failed_inserts = 0
            
            for i, item in enumerate(data, 1):
                try:
                    await collection.data.insert(properties=item["properties"])
                    successful_inserts += 1
                    if i % 100 == 0:
                        print(f"Progress: {i}/{total_records} records inserted")
                except Exception as e:
                    failed_inserts += 1
                    print(f"Error inserting item into {collection_name}: {str(e)}")
                    print(f"Problematic item: {json.dumps(item, indent=2)}")
            
            print(f"\nInsertion complete for {collection_name}:")
            print(f"- Successful inserts: {successful_inserts}")
            print(f"- Failed inserts: {failed_inserts}")
            print(f"- Success rate: {(successful_inserts/total_records)*100:.2f}%")
        
        except Exception as e:
            print(f"Error creating {collection_name} collection: {str(e)}")
            raise

    return collections

async def run_queries(client, queries_data: List[Dict], collections: Dict):
    """Run queries against the pre-loaded collections."""
    successful_queries = 0
    failed_queries = 0

    for idx, query_data in enumerate(queries_data):
        try:
            print(f"\nProcessing query {idx + 1}/{len(queries_data)}")
            
            # Get query info
            query_info = query_data['query']

            # TODO: Be careful here with collection routing interface
            target_collection = query_info['target_collection']
            
            if target_collection not in collections:
                raise ValueError(f"Target collection {target_collection} not found")
            
            # Get properties for the target collection
            schema_data = parse_schema(query_data['database_schema'])
            collection_def = next(
                c for c in schema_data['weaviate_collections'] 
                if c['name'] == target_collection
            )
            view_properties = [p['name'] for p in collection_def['properties']]
            
            # Create agent
            agent = await WeaviateSearchAgentSimple.create(
                query=query_info['corresponding_natural_language_query'],
                collections=collections[target_collection],
                tenant=None,
                collection_view_properties=view_properties
            )
            
            # Run query
            print("\nRunning query:", query_info['corresponding_natural_language_query'])
            result = await agent.run(agent.query)
            
            # Print results
            print("\nQuery results:")
            print("Original Query:", result.original_query)
            print("Search Queries sent:", result.searches)
            print("Aggregation Queries sent:", result.aggregations)
            print("Final Answer:", result.final_answer)
            print("Usage Stats:", result.usage)
            
            successful_queries += 1
            
        except Exception as e:
            print(f"\nError processing query {idx + 1}: {str(e)}")
            failed_queries += 1

    return {
        "total_queries": len(queries_data),
        "successful_queries": successful_queries,
        "failed_queries": failed_queries
    }

async def run_benchmark(queries_file: str):
    """Run the benchmark with proper schema setup."""
    print("\nStarting benchmark run...")
    
    # Load test queries
    with open(queries_file, 'r') as f:
        queries_data = json.load(f)
        print(f"\nLoaded {len(queries_data)} queries")

    # Get unique collections from all queries
    unique_collections = {}
    for query_data in queries_data:
        schema_data = parse_schema(query_data['database_schema'])
        for collection in schema_data.get('weaviate_collections', []):
            unique_collections[collection['name']] = collection

    # Initialize client
    print("\nInitializing Weaviate client...")
    client = weaviate.use_async_with_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
        headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
    )

    try:
        # Connect to client
        await client.connect()
        print("Connected to Weaviate")

        # Setup all unique collections first
        schema_data = {'weaviate_collections': list(unique_collections.values())}
        collections = await setup_collections(client, schema_data)

        # Run all queries against the pre-loaded collections
        result = await run_queries(client, queries_data, collections)

        # Clean up all collections at the end
        for collection_name in unique_collections:
            if client.collections.exists(collection_name):
                await client.collections.delete(collection_name)

        return result

    finally:
        print("\nClosing Weaviate connection...")
        await client.close()

async def main():
    try:
        print("Starting benchmark test...")
        result = await run_benchmark("../../data/synthetic-weaviate-queries-with-results.json")
        print("\n=== Benchmark Summary ===")
        print(f"Total Queries: {result['total_queries']}")
        print(f"Successful: {result['successful_queries']}")
        print(f"Failed: {result['failed_queries']}")
        print("=========================")
    except Exception as e:
        print(f"\nBenchmark failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())