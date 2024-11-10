# Create Weaviate Collections from JSON schema files

```python
import requests

url = "http://localhost:8080/v1/schema"

# Post each class schema separately
for class_schema in json_schema['weaviate_collections']:
    # Make sure the schema has all required fields
    if 'class' not in class_schema:
        print("Error: Schema missing required 'class' field")
        continue
        
    # Create a clean schema object with only the required fields
    clean_schema = {
        'class': class_schema['class'],  # Use existing 'class' field
        'description': class_schema.get('description', ''),
        'properties': [
            {
                'name': prop['name'],
                'description': prop.get('description', ''),
                'dataType': prop['data_type']  # Weaviate expects dataType, not data_type
            }
            for prop in class_schema.get('properties', [])
        ],
        'vectorizer': class_schema.get('vectorizer', 'text2vec-transformers'),
        'vectorIndexType': class_schema.get('vectorIndexType', 'hnsw'),
    }
    
    # Convert to string
    schema_str = json.dumps(clean_schema)
    
    print(f"Sending schema for class {clean_schema['class']}:")
    print(schema_str)
    
    response = requests.post(
        url, 
        data=schema_str,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Response status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error response: {response.text}")
```
