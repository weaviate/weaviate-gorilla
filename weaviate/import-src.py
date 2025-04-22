import os
import weaviate
import weaviate.classes as wvc
from pathlib import Path
from weaviate.agents.transformation import TransformationAgent
from weaviate.agents.classes import Operations
from weaviate.collections.classes.config import DataType

# Configuration
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WEAVIATE_URL = os.environ.get("WEAVIATE_URL", "")  # Get Weaviate URL from environment
WEAVIATE_API_KEY = os.environ.get("WEAVIATE_API_KEY", "")  # Get Weaviate API key from environment
SRC_DIR = os.environ.get("SRC_DIR", "../src")  # Path to your source code directory

def connect_to_weaviate():
    print("Connecting to Weaviate...")
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
    )
    print("Successfully connected to Weaviate")
    return client

def setup_schema(client):
    # Delete existing collection if it exists
    collection_name = "CodeFiles"
    if client.collections.exists(collection_name):
        client.collections.delete(collection_name)
        print(f"Deleted existing {collection_name} collection")

    # Create new collection
    print("Creating CodeFiles collection...")
    code_collection = client.collections.create(
        name=collection_name,
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_weaviate(),
        properties=[
            wvc.config.Property(
                name="parent_folder_name",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="filename",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="content",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="content_summary",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=False,
            )
        ],
    )
    print("Successfully created CodeFiles collection")
    return code_collection

def import_code_files(code_collection):
    print(f"Starting to import files from {SRC_DIR}...")
    total_files = 0
    
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.startswith('.') or file.endswith('.pyc') or file.endswith('.json') or file.endswith('.md'):
                continue
                
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, SRC_DIR)
            parent_folder = os.path.dirname(relative_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Prepare the data object
                    data_object = {
                        "parent_folder_name": parent_folder,
                        "filename": file,
                        "content": content
                    }
                    
                    # Insert into Weaviate
                    code_collection.data.insert(properties=data_object)
                    total_files += 1
                    print(f"Imported: {relative_path}")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
    
    print(f"\nImport completed. Total files imported: {total_files}")

def generate_content_summaries(client):
    print("Generating content summaries for code files...")
    
    create_summary = Operations.update_property(
        property_name="content_summary",
        view_properties=["content", "filename", "parent_folder_name"],
        instruction="Generate a comprehensive summary of this code file. Describe its purpose, main functions, and how it fits into the overall project structure. Focus on technical details that would be relevant for someone trying to understand the codebase."
    )
    
    agent = TransformationAgent(
        client=client,
        collection="CodeFiles",
        operations=[create_summary],
    )
    
    response = agent.update_all()

def main():
    client = connect_to_weaviate()
    code_collection = setup_schema(client)
    import_code_files(code_collection)
    generate_content_summaries(client)
    client.close()

if __name__ == "__main__":
    main()
