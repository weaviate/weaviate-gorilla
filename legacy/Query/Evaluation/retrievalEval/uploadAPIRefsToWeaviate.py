import weaviate
from weaviate.util import get_valid_uuid
from uuid import uuid4
import os

client = weaviate.Client("http://localhost:8080")

schema = {
    "classes": [
        {
            "class": "APIReference",
            "description": "Descriptions of Weaviate's GraphQL Search APIs.",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
               "reranker-cohere": { 
                    "model": "rerank-multilingual-v2.0"
                }
            },
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The content of the API reference.",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False
                        }
                    },
                },
                {
                    "name": "apiRefPath",
                    "dataType": ["text"],
                    "description": "The file path used to identify the api.",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": True,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False
                        }
                    }
                }
            ]
        }
    ]
}

client.schema.create(schema)

def readTxtFile(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    return content

for apiPath in os.listdir("../dataEngine/data/APIref"):
    if "DS_Store" not in apiPath:
        apiRef = readTxtFile("../dataEngine/data/APIref/"+apiPath)
        props = {
            "content": apiRef,
            "apiRefPath": apiPath
        }
        apiRefUUID = get_valid_uuid(uuid4())
        client.data_object.create(
            data_object=props,
            class_name="APIReference",
            uuid=apiRefUUID
        )