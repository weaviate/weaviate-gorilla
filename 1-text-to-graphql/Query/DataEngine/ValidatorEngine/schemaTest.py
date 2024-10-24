import json
import weaviate
client = weaviate.Client("http://localhost:8080")

def json_reader(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as api_ref_fh:
        data = json.load(api_ref_fh)
    return data

schema = json_reader("../data/ToySchemas/candles.json")
client.schema.delete_all()
client.schema.create(schema)