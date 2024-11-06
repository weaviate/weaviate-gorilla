import weaviate
from weaviate.classes.query import Filter

def get_collections_info(client: weaviate.WeaviateClient) -> tuple[str, list[str]]:
    """
    Get detailed information about all collections in a Weaviate instance.
    
    Args:
        client: A Weaviate client instance
    
    Returns:
        tuple[str, list[str]]: Tuple containing formatted collection details string and list of collection names
    """
    
    collections = client.collections.list_all()
    
    # Get collection names as list
    collection_names = list(collections.keys())
    
    # Build output string
    output = []
    for collection_name, config in collections.items():
        output.append(f"\nCollection Name: {collection_name}")
        output.append(f"Description: {config.description}")
        output.append("\nProperties:")
        for prop in config.properties:
            output.append(f"- {prop.name}: {prop.description} (type: {prop.data_type.value})")
    
    return "\n".join(output), collection_names

def _build_weaviate_filter(filter_string: str) -> Filter:
    def _parse_condition(condition: str) -> Filter:
        parts = condition.split(':')
        if len(parts) < 3:
            raise ValueError(f"Invalid condition: {condition}")
        
        property, operator, value = parts[0], parts[1], ':'.join(parts[2:])
        
        if operator == '==':
            return Filter.by_property(property).equal(value)
        elif operator == '!=':
            return Filter.by_property(property).not_equal(value)
        elif operator == '>':
            return Filter.by_property(property).greater_than(float(value))
        elif operator == '<':
            return Filter.by_property(property).less_than(float(value))
        elif operator == '>=':
            return Filter.by_property(property).greater_than_equal(float(value))
        elif operator == '<=':
            return Filter.by_property(property).less_than_equal(float(value))
        elif operator == 'LIKE':
            return Filter.by_property(property).like(value)
        elif operator == 'CONTAINS_ANY':
            return Filter.by_property(property).contains_any(value.split(','))
        elif operator == 'CONTAINS_ALL':
            return Filter.by_property(property).contains_all(value.split(','))
        elif operator == 'WITHIN':
            lat, lon, dist = map(float, value.split(','))
            return Filter.by_property(property).within_geo_range(lat, lon, dist)
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def _parse_group(group: str) -> Filter:
        if 'AND' in group:
            conditions = [_parse_group(g.strip()) for g in group.split('AND')]
            return Filter.all_of(conditions)
        elif 'OR' in group:
            conditions = [_parse_group(g.strip()) for g in group.split('OR')]
            return Filter.any_of(conditions)
        else:
            return _parse_condition(group)

    # Remove outer parentheses if present
    filter_string = filter_string.strip()
    if filter_string.startswith('(') and filter_string.endswith(')'):
        filter_string = filter_string[1:-1]

    return _parse_group(filter_string)