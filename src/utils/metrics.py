from src.models import (
    WeaviateQuery,
    WeaviateQueryWithSchema
)

def abstract_syntax_tree_match_score(
        predicted_apis: WeaviateQuery,
        ground_truth: WeaviateQueryWithSchema
    ) -> float:
    """
    Calculate a matching score between predicted and ground truth WeaviateQuery objects.
    Returns a float between 0.0 and 1.0, where 1.0 indicates a perfect match.
    """
    score = 0.0
    
    # Weight definitions for different components
    weights = {
        'target_collection': 0.2,
        'search_query': 0.2,
        'filters': 0.2,
        'aggregations': 0.2,
        'groupby': 0.2
    }
    
    # Check target collection match (exact match required)
    if predicted_apis.target_collection == ground_truth.target_collection:
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