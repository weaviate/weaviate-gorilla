# Configuration
import os
from dotenv import load_dotenv
import weaviate
from weaviate.agents.query import QueryAgent

# Load environment variables
load_dotenv()

WEAVIATE_URL = os.environ.get("WEAVIATE_URL", "")  # Get Weaviate URL from environment
WEAVIATE_API_KEY = os.environ.get("WEAVIATE_API_KEY", "")  # Get Weaviate API key from environment
SRC_DIR = os.environ.get("SRC_DIR", "../src")  # Path to your source code directory

print(WEAVIATE_URL)

def connect_to_weaviate():
    print("Connecting to Weaviate...")
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
    )
    print("Successfully connected to Weaviate")
    return client

client = connect_to_weaviate()

qa = QueryAgent(
    client=client, 
    collections=["CodeFiles"]
)

print(qa.run(
    "How many CodeFiles are in the collection?"
).final_answer)

print(qa.run(
    "What LLMs does the CodeFiles repo support?"
).final_answer)

print(qa.run(
    "How can I extend my code to add a required thinking before predicting the database query?"
).final_answer)