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
    print("\033[92m=== Calculating AST Match Score ===\033[0m")
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
    print(f"\033[92mComparing target collections:\033[0m")
    print(f"Predicted: {predicted_apis.target_collection}")
    print(f"Ground Truth: {ground_truth.target_collection}")
    if predicted_apis.target_collection == ground_truth.target_collection:
        score += weights['target_collection']
        print(f"\033[92mTarget collection match! Score: +{weights['target_collection']}\033[0m")
    
    # Check search query match (if both have search queries)
    print(f"\033[92mComparing search queries:\033[0m")
    print(f"Predicted: {predicted_apis.search_query}")
    print(f"Ground Truth: {ground_truth.search_query}")
    if predicted_apis.search_query and ground_truth.search_query:
        if predicted_apis.search_query.lower() == ground_truth.search_query.lower():
            score += weights['search_query']
            print(f"\033[92mSearch query match! Score: +{weights['search_query']}\033[0m")
    elif predicted_apis.search_query is None and ground_truth.search_query is None:
        score += weights['search_query']  # Both None is also a match
        print(f"\033[92mBoth search queries are None! Score: +{weights['search_query']}\033[0m")
    
    # Check filters match
    print("\033[92m=== Checking Filters ===\033[0m")
    filter_score = 0.0
    filter_count = 0
    
    # Integer filter check
    if predicted_apis.integer_property_filter is None and ground_truth.integer_property_filter is None:
        filter_score += 1
        filter_count += 1
        print("\033[92mBoth integer filters are None - match!\033[0m")
    elif predicted_apis.integer_property_filter and ground_truth.integer_property_filter:
        if (predicted_apis.integer_property_filter.property_name == ground_truth.integer_property_filter.property_name and
            predicted_apis.integer_property_filter.operator == ground_truth.integer_property_filter.operator and
            predicted_apis.integer_property_filter.value == ground_truth.integer_property_filter.value):
            filter_score += 1
            print("\033[92mInteger filters match!\033[0m")
        filter_count += 1
        
    # Text filter check
    if predicted_apis.text_property_filter is None and ground_truth.text_property_filter is None:
        filter_score += 1
        filter_count += 1
        print("\033[92mBoth text filters are None - match!\033[0m")
    elif predicted_apis.text_property_filter and ground_truth.text_property_filter:
        if (predicted_apis.text_property_filter.property_name == ground_truth.text_property_filter.property_name and
            predicted_apis.text_property_filter.operator == ground_truth.text_property_filter.operator and
            predicted_apis.text_property_filter.value == ground_truth.text_property_filter.value):
            filter_score += 1
            print("\033[92mText filters match!\033[0m")
        filter_count += 1
        
    # Boolean filter check
    if predicted_apis.boolean_property_filter is None and ground_truth.boolean_property_filter is None:
        filter_score += 1
        filter_count += 1
        print("\033[92mBoth boolean filters are None - match!\033[0m")
    elif predicted_apis.boolean_property_filter and ground_truth.boolean_property_filter:
        if (predicted_apis.boolean_property_filter.property_name == ground_truth.boolean_property_filter.property_name and
            predicted_apis.boolean_property_filter.operator == ground_truth.boolean_property_filter.operator and
            predicted_apis.boolean_property_filter.value == ground_truth.boolean_property_filter.value):
            filter_score += 1
            print("\033[92mBoolean filters match!\033[0m")
        filter_count += 1
    
    if filter_count > 0:
        filter_contribution = weights['filters'] * (filter_score / filter_count)
        score += filter_contribution
        print(f"\033[92mFilter contribution to score: +{filter_contribution:.3f}\033[0m")
    
    # Check aggregations match
    print("\033[92m=== Checking Aggregations ===\033[0m")
    agg_score = 0.0
    agg_count = 0
    
    # Integer aggregation check
    if predicted_apis.integer_property_aggregation is None and ground_truth.integer_property_aggregation is None:
        agg_score += 1
        agg_count += 1
        print("\033[92mBoth integer aggregations are None - match!\033[0m")
    elif predicted_apis.integer_property_aggregation and ground_truth.integer_property_aggregation:
        if (predicted_apis.integer_property_aggregation.property_name == ground_truth.integer_property_aggregation.property_name and
            predicted_apis.integer_property_aggregation.metrics == ground_truth.integer_property_aggregation.metrics):
            agg_score += 1
            print("\033[92mInteger aggregations match!\033[0m")
        agg_count += 1
        
    # Text aggregation check
    if predicted_apis.text_property_aggregation is None and ground_truth.text_property_aggregation is None:
        agg_score += 1
        agg_count += 1
        print("\033[92mBoth text aggregations are None - match!\033[0m")
    elif predicted_apis.text_property_aggregation and ground_truth.text_property_aggregation:
        if (predicted_apis.text_property_aggregation.property_name == ground_truth.text_property_aggregation.property_name and
            predicted_apis.text_property_aggregation.metrics == ground_truth.text_property_aggregation.metrics):
            agg_score += 1
            print("\033[92mText aggregations match!\033[0m")
        agg_count += 1
        
    # Boolean aggregation check
    if predicted_apis.boolean_property_aggregation is None and ground_truth.boolean_property_aggregation is None:
        agg_score += 1
        agg_count += 1
        print("\033[92mBoth boolean aggregations are None - match!\033[0m")
    elif predicted_apis.boolean_property_aggregation and ground_truth.boolean_property_aggregation:
        if (predicted_apis.boolean_property_aggregation.property_name == ground_truth.boolean_property_aggregation.property_name and
            predicted_apis.boolean_property_aggregation.metrics == ground_truth.boolean_property_aggregation.metrics):
            agg_score += 1
            print("\033[92mBoolean aggregations match!\033[0m")
        agg_count += 1
    
    if agg_count > 0:
        agg_contribution = weights['aggregations'] * (agg_score / agg_count)
        score += agg_contribution
        print(f"\033[92mAggregation contribution to score: +{agg_contribution:.3f}\033[0m")
    
    # Check groupby match
    print("\033[92m=== Checking GroupBy ===\033[0m")
    print(f"Predicted GroupBy: {predicted_apis.groupby_property}")
    print(f"Ground Truth GroupBy: {ground_truth.groupby_property}")
    if predicted_apis.groupby_property == ground_truth.groupby_property:
        score += weights['groupby']
        print(f"\033[92mGroupBy match! Score: +{weights['groupby']}\033[0m")
    
    print(f"\033[92mFinal AST Match Score: {score:.3f}\033[0m")
    return score