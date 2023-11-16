import weaviate

client = weaviate.Client("http://localhost:8080")

schema = {
    "classes": [
        {
            "class": "Document",
            "description": "A BEIR document.",
            "moduleConfig": {
                "text2vec-cohere": {
                    "skip": False,
                    "vectorizeClassName": False,
                    "vectorizePropertyName": False
                }
            },
            "vectorIndexType": "hnsw",
            "vectorizer": "text2vec-cohere",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The text content in the BEIR document.",
                    "moduleConfig": {
                        "text2vec-cohere": {
                            "skip": False,
                            "vectorizePropertyName": False,
                            "vectorizeClassName": False
                        }
                    }
                },
                {
                    "name": "DocID",
                    "dataType": ["int"],
                    "description": "The Document ID (these are mapped from the original BEIR doc ids to a sequential index).",
                    "moduleConfig": {
                        "text2vec-transformers": {
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