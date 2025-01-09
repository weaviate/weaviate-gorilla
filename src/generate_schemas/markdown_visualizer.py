from src.models import WeaviateCollectionConfig, Property
import json

with open("3-collection-schemas-with-search-property.json", "r") as file:
    schemas = json.load(file)

# Generate markdown table
markdown_content = "# Generated Database Schemas\n\n"

for idx, schema_set in enumerate(schemas):
    markdown_content += f"## Schema Set {idx + 1}\n\n"
    
    # Parse the JSON string back into a dict if needed
    if isinstance(schema_set, str):
        schema_set = json.loads(schema_set)
    
    # Access the collections
    collections = schema_set.get('weaviate_collections', schema_set)
    
    # Get overview from first collection
    if isinstance(collections, list) and len(collections) > 0:
        if isinstance(collections[0], WeaviateCollectionConfig):
            markdown_content += f"**Overview:** {collections[0].envisioned_use_case_overview}\n\n"
        elif isinstance(collections[0], dict):
            markdown_content += f"**Overview:** {collections[0].get('envisioned_use_case_overview', '')}\n\n"
    
    for collection in collections:
        if isinstance(collection, WeaviateCollectionConfig):
            name = collection.name
            properties = collection.properties
            use_case = collection.envisioned_use_case_overview
        elif isinstance(collection, dict):
            name = collection.get('name', '')
            properties = collection.get('properties', [])
            use_case = collection.get('envisioned_use_case_overview', '')
            
        markdown_content += f"### {name}\n\n"
        markdown_content += "| Property | Type | Description |\n"
        markdown_content += "|----------|------|-------------|\n"
        
        for prop in properties:
            if isinstance(prop, Property):
                prop_name = prop.name
                prop_type = prop.data_type[0]
                prop_desc = prop.description
            elif isinstance(prop, dict):
                prop_name = prop.get('name', '')
                prop_type = prop.get('data_type', [''])[0]
                prop_desc = prop.get('description', '')
                
            markdown_content += f"| {prop_name} | {prop_type} | {prop_desc} |\n"
        
        markdown_content += f"\n**Use Case:** {use_case}\n\n"
    
    markdown_content += "---\n\n"

# Save markdown
with open("generated_schemas.md", "w+") as file:
    file.write(markdown_content)