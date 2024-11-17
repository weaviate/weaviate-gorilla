from src.models import WeaviateQuery

def pretty_print_weaviate_query(query: WeaviateQuery) -> None:
    """Pretty prints a WeaviateQuery object with color and indentation."""
    print("\n\033[92mWeaviate Query Details:\033[0m")
    print(f"  \033[92mTarget Collection:\033[0m {query.target_collection}")
    print(f"  \033[92mSearch Query:\033[0m {query.search_query}")
    
    if query.integer_property_filter:
        print("  \033[92mInteger Filter:\033[0m")
        print(f"    Property: {query.integer_property_filter.property_name}")
        print(f"    Operator: {query.integer_property_filter.operator}")
        print(f"    Value: {query.integer_property_filter.value}")
    
    if query.text_property_filter:
        print("  \033[92mText Filter:\033[0m")
        print(f"    Property: {query.text_property_filter.property_name}")
        print(f"    Operator: {query.text_property_filter.operator}")
        print(f"    Value: {query.text_property_filter.value}")
        
    if query.boolean_property_filter:
        print("  \033[92mBoolean Filter:\033[0m")
        print(f"    Property: {query.boolean_property_filter.property_name}")
        print(f"    Operator: {query.boolean_property_filter.operator}")
        print(f"    Value: {query.boolean_property_filter.value}")
        
    if query.integer_property_aggregation:
        print("  \033[92mInteger Aggregation:\033[0m")
        print(f"    Property: {query.integer_property_aggregation.property_name}")
        print(f"    Metrics: {query.integer_property_aggregation.metrics}")
        
    if query.text_property_aggregation:
        print("  \033[92mText Aggregation:\033[0m")
        print(f"    Property: {query.text_property_aggregation.property_name}")
        print(f"    Metrics: {query.text_property_aggregation.metrics}")
        
    if query.boolean_property_aggregation:
        print("  \033[92mBoolean Aggregation:\033[0m")
        print(f"    Property: {query.boolean_property_aggregation.property_name}")
        print(f"    Metrics: {query.boolean_property_aggregation.metrics}")
        
    if query.groupby_property:
        print(f"  \033[92mGroup By:\033[0m {query.groupby_property}")
        
    print(f"  \033[92mNatural Language Query:\033[0m {query.corresponding_natural_language_query}")

print("\033[92m=== Loading Weaviate Queries ===\033[0m")