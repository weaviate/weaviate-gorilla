from src.models import (
    WeaviateQuery,
    WeaviateQueryWithSchema
)

def abstract_syntax_tree_match_score(
        predicted_apis: WeaviateQuery,
        ground_truth: WeaviateQueryWithSchema
    ) -> float:
    """
    Calculate a matching score between predicted and ground truth WeaviateQuery objects using
    Abstract Syntax Tree (AST) matching principles.

    AST matching evaluates structural similarity between two trees by comparing nodes in a 
    hierarchical manner. For Weaviate queries, this means:

    1. Root Node (Collection) - The target_collection is the root node and must match first.
       If collections don't match, the entire tree is considered invalid (score of 0).
    
    2. Primary Branches - If root matches, we evaluate primary query components:
       - Search query (text match)
       - Filters (property name, operator, value match)
       - Aggregations (property name, metrics match) 
       - Group by (property name match)

    The weighting is intentionally biased toward correct collection selection:
    - target_collection: 0.4 (required for any other points)
    - search_query: 0.15
    - filters: 0.15  
    - aggregations: 0.15
    - groupby: 0.15

    Args:
        predicted_apis: The WeaviateQuery predicted by the model
        ground_truth: The known correct WeaviateQueryWithSchema to compare against

    Returns:
        float: Score between 0.0 and 1.0, where:
            0.0 = Complete mismatch starting at root (collection)
            1.0 = Perfect structural match across all nodes
    """
    score = 0.0
    
    # Weight definitions for different components
    weights = {
        'target_collection': 0.4,  # Increased weight for collection
        'search_query': 0.15,
        'filters': 0.15,
        'aggregations': 0.15,
        'groupby': 0.15
    }
    
    # Check target collection match (exact match required)
    # If this fails, return 0 as the AST root node is incorrect
    if predicted_apis.target_collection != ground_truth.target_collection:
        print(f"\033[92mFinal AST Match Score: 0.000 (Collection mismatch)\033[0m")
        return 0.0
    
    score += weights['target_collection']
    
    # Check search query match (if both have search queries)
    if predicted_apis.search_query and ground_truth.search_query:
        if predicted_apis.search_query.lower() == ground_truth.search_query.lower():
            score += weights['search_query']
    elif predicted_apis.search_query is None and ground_truth.search_query is None:
        score += weights['search_query']  # Both None is also a match
    
    # Check filters match
    filter_score = 0.0
    filter_count = 0
    
    # Integer filter check
    if predicted_apis.integer_property_filter is None and ground_truth.integer_property_filter is None:
        filter_score += 1
        filter_count += 1
    elif predicted_apis.integer_property_filter and ground_truth.integer_property_filter:
        if (predicted_apis.integer_property_filter.property_name == ground_truth.integer_property_filter.property_name and
            predicted_apis.integer_property_filter.operator == ground_truth.integer_property_filter.operator and
            predicted_apis.integer_property_filter.value == ground_truth.integer_property_filter.value):
            filter_score += 1
        filter_count += 1
        
    # Text filter check
    if predicted_apis.text_property_filter is None and ground_truth.text_property_filter is None:
        filter_score += 1
        filter_count += 1
    elif predicted_apis.text_property_filter and ground_truth.text_property_filter:
        if (predicted_apis.text_property_filter.property_name == ground_truth.text_property_filter.property_name and
            predicted_apis.text_property_filter.operator == ground_truth.text_property_filter.operator and
            predicted_apis.text_property_filter.value == ground_truth.text_property_filter.value):
            filter_score += 1
        filter_count += 1
        
    # Boolean filter check
    if predicted_apis.boolean_property_filter is None and ground_truth.boolean_property_filter is None:
        filter_score += 1
        filter_count += 1
    elif predicted_apis.boolean_property_filter and ground_truth.boolean_property_filter:
        if (predicted_apis.boolean_property_filter.property_name == ground_truth.boolean_property_filter.property_name and
            predicted_apis.boolean_property_filter.operator == ground_truth.boolean_property_filter.operator and
            predicted_apis.boolean_property_filter.value == ground_truth.boolean_property_filter.value):
            filter_score += 1
        filter_count += 1
    
    if filter_count > 0:
        filter_contribution = weights['filters'] * (filter_score / filter_count)
        score += filter_contribution
    
    # Check aggregations match
    agg_score = 0.0
    agg_count = 0
    
    # Integer aggregation check
    if predicted_apis.integer_property_aggregation is None and ground_truth.integer_property_aggregation is None:
        agg_score += 1
        agg_count += 1
    elif predicted_apis.integer_property_aggregation and ground_truth.integer_property_aggregation:
        if (predicted_apis.integer_property_aggregation.property_name == ground_truth.integer_property_aggregation.property_name and
            predicted_apis.integer_property_aggregation.metrics == ground_truth.integer_property_aggregation.metrics):
            agg_score += 1
        agg_count += 1
        
    # Text aggregation check
    if predicted_apis.text_property_aggregation is None and ground_truth.text_property_aggregation is None:
        agg_score += 1
        agg_count += 1
    elif predicted_apis.text_property_aggregation and ground_truth.text_property_aggregation:
        if (predicted_apis.text_property_aggregation.property_name == ground_truth.text_property_aggregation.property_name and
            predicted_apis.text_property_aggregation.metrics == ground_truth.text_property_aggregation.metrics):
            agg_score += 1
        agg_count += 1
        
    # Boolean aggregation check
    if predicted_apis.boolean_property_aggregation is None and ground_truth.boolean_property_aggregation is None:
        agg_score += 1
        agg_count += 1
    elif predicted_apis.boolean_property_aggregation and ground_truth.boolean_property_aggregation:
        if (predicted_apis.boolean_property_aggregation.property_name == ground_truth.boolean_property_aggregation.property_name and
            predicted_apis.boolean_property_aggregation.metrics == ground_truth.boolean_property_aggregation.metrics):
            agg_score += 1
        agg_count += 1
    
    if agg_count > 0:
        agg_contribution = weights['aggregations'] * (agg_score / agg_count)
        score += agg_contribution
    
    # Check groupby match
    if predicted_apis.groupby_property == ground_truth.groupby_property:
        score += weights['groupby']
    
    print(f"\033[92mFinal AST Match Score: {score:.3f}\033[0m")
    return score