from typing import Any
import weaviate
import weaviate.classes as wvc
from weaviate.classes.query import Filter
from src.models import WeaviateQuery

def execute_weaviate_query(
    weaviate_client: weaviate.WeaviateClient,
    predicted_query: WeaviateQuery
) -> str:
    """Execute a predicted WeaviateQuery and return formatted results."""
    
    # Convert WeaviateQuery to tool args format
    tool_args = {
        "collection_name": predicted_query.target_collection,
    }
    
    if predicted_query.search_query:
        tool_args["search_query"] = predicted_query.search_query
        
    if predicted_query.integer_property_filter:
        tool_args["integer_property_filter"] = predicted_query.integer_property_filter.model_dump()
        
    if predicted_query.text_property_filter:
        tool_args["text_property_filter"] = predicted_query.text_property_filter.model_dump()
        
    if predicted_query.boolean_property_filter:
        tool_args["boolean_property_filter"] = predicted_query.boolean_property_filter.model_dump()
        
    if predicted_query.integer_property_aggregation:
        tool_args["integer_property_aggregation"] = predicted_query.integer_property_aggregation.model_dump()
        
    if predicted_query.text_property_aggregation:
        tool_args["text_property_aggregation"] = predicted_query.text_property_aggregation.model_dump()
        
    if predicted_query.boolean_property_aggregation:
        tool_args["boolean_property_aggregation"] = predicted_query.boolean_property_aggregation.model_dump()
        
    if predicted_query.groupby_property:
        tool_args["groupby_property"] = predicted_query.groupby_property

    # Execute query based on type
    if _is_aggregation_query(tool_args):
        final_response = _handle_aggregation_query(weaviate_client, tool_args)
    elif "search_query" in tool_args:
        final_response = _handle_search_query(weaviate_client, tool_args)
    else:
        final_response = _handle_filter_query(weaviate_client, tool_args)

    return final_response

def _is_aggregation_query(tool_args: dict) -> bool:
    return any(key.endswith("_aggregation") for key in tool_args.keys())

def _handle_aggregation_query(
    weaviate_client: weaviate.WeaviateClient, 
    tool_args: dict
) -> str:
    collection_name = tool_args["collection_name"]
    collection = weaviate_client.collections.get(collection_name)

    agg_args = _build_aggregation_args(tool_args)

    if "search_query" in tool_args:
        return _execute_aggregation_with_search(collection, tool_args, agg_args)
    else:
        return _execute_aggregation_over_all(collection, agg_args)

def _build_aggregation_args(tool_args: dict) -> dict:
    agg_args: dict = {"total_count": True}

    if "groupby_property" in tool_args:
        agg_args["group_by"] = tool_args["groupby_property"]

    agg_args["return_metrics"] = _build_return_metrics(tool_args)

    return agg_args

def _build_return_metrics(tool_args: dict):
    metrics_types = [
        "integer_property_aggregation",
        "text_property_aggregation", 
        "boolean_property_aggregation"
    ]

    for agg_type in metrics_types:
        if agg_type in tool_args:
            prop_name = tool_args[agg_type]["property_name"]
            metrics = tool_args[agg_type]["metrics"].upper()
            if prop_name:
                if agg_type.startswith("integer"):
                    # Map to correct integer metric names
                    metric_mapping = {
                        "MEAN": "mean",
                        "SUM": "sum_",
                        "MAX": "maximum",
                        "MIN": "minimum",
                        "COUNT": "count"
                    }
                    metric_name = metric_mapping.get(metrics, metrics.lower())
                    return wvc.query.Metrics(prop_name).integer(**{metric_name: True})
                    
                elif agg_type.startswith("text"):
                    # Map to correct text metric names
                    if metrics == "COUNT":
                        return wvc.query.Metrics(prop_name).text(count=True)
                    elif metrics == "TOP_OCCURRENCES":
                        return wvc.query.Metrics(prop_name).text(
                            top_occurrences_count=True,
                            top_occurrences_value=True
                        )
                    
                elif agg_type.startswith("boolean"):
                    # Map to correct boolean metric names
                    if metrics == "PERCENTAGE_TRUE":
                        return wvc.query.Metrics(prop_name).boolean(percentage_true=True)
                    elif metrics == "COUNT":
                        return wvc.query.Metrics(prop_name).boolean(count=True)
                    else:
                        return wvc.query.Metrics(prop_name).boolean(**{metrics.lower(): True})
    return None

def _execute_aggregation_with_search(
    collection,
    tool_args: dict,
    agg_args: dict
) -> str:
    if agg_args.get("return_metrics"):
        response = collection.aggregate.near_text(
            query=tool_args["search_query"],
            object_limit=5,
            total_count=agg_args["total_count"],
            group_by=agg_args.get("group_by"),
            return_metrics=agg_args["return_metrics"]
        )
    else:
        response = collection.query.hybrid(
            query=tool_args["search_query"],
            limit=5
        )
    return _format_query_result(response)

def _execute_aggregation_over_all(collection, agg_args: dict) -> str:
    response = collection.aggregate.over_all(
        total_count=agg_args["total_count"],
        group_by=agg_args.get("group_by"),
        return_metrics=agg_args.get("return_metrics")
    )
    return _format_query_result(response)

def _handle_search_query(
    weaviate_client: weaviate.WeaviateClient,
    tool_args: dict
) -> str:
    collection_name = tool_args["collection_name"]
    collection = weaviate_client.collections.get(collection_name)

    response = collection.query.hybrid(
        query=tool_args["search_query"],
        limit=5
    )
    return _format_query_result(response)

def _handle_filter_query(
    weaviate_client: weaviate.WeaviateClient,
    tool_args: dict
) -> str:
    collection_name = tool_args["collection_name"]
    collection = weaviate_client.collections.get(collection_name)

    combined_filter = _build_filters(tool_args)
    response = collection.query.fetch_objects(
        limit=5,
        filters=combined_filter
    )
    return _format_query_result(response)

def _build_filters(tool_args: dict):
    filters = []
    for filter_type in [
        "integer_property_filter",
        "text_property_filter",
        "boolean_property_filter"
    ]:
        if filter_type in tool_args:
            prop_name = tool_args[filter_type]["property_name"]
            operator = tool_args[filter_type]["operator"]
            value = tool_args[filter_type]["value"]

            if filter_type == "boolean_property_filter":
                if isinstance(value, str):
                    value = value.lower() == 'true'

            filter_obj = Filter.by_property(prop_name)
            if operator == "=":
                filters.append(filter_obj.equal(value))
            elif operator == "!=":
                filters.append(filter_obj.not_equal(value))
            elif operator == ">":
                filters.append(filter_obj.greater_than(value))
            elif operator == "<":
                filters.append(filter_obj.less_than(value))
            elif operator == ">=":
                filters.append(filter_obj.greater_or_equal(value))
            elif operator == "<=":
                filters.append(filter_obj.less_or_equal(value))
            elif operator == "LIKE":
                filters.append(filter_obj.like(value))

    if len(filters) > 1:
        combined = filters[0]
        for f in filters[1:]:
            combined = combined & f
        return combined
    elif len(filters) == 1:
        return filters[0]
    return None

def _format_query_result(result: Any) -> str:
    """Format query results into a readable string."""
    
    # Handle QueryReturn objects (regular search/filter queries)
    if hasattr(result, "objects"):
        formatted = "Found objects:\n"
        for obj in result.objects:
            formatted += "-" * 40 + "\n"
            for key, value in obj.properties.items():
                formatted += f"{key}: {value}\n"
        return formatted

    # Handle AggregateReturn objects (simple aggregations)
    elif hasattr(result, "properties"):
        formatted = "Aggregation results:\n"
        formatted += "-" * 40 + "\n"
        for prop_name, metrics in result.properties.items():
            formatted += f"Property: {prop_name}\n"
            for metric_name, value in metrics.__dict__.items():
                if value is not None:
                    if metric_name == "top_occurrences":
                        formatted += f"  Most common values:\n"
                        for occurrence in value:
                            formatted += f"    - {occurrence.value} (count: {occurrence.count})\n"
                    else:
                        formatted += f"  {metric_name}: {value}\n"
        if hasattr(result, "total_count"):
            formatted += f"Total count: {result.total_count}\n"
        return formatted

    # Handle AggregateGroupByReturn objects (grouped aggregations)
    elif hasattr(result, "groups"):
        formatted = "Grouped aggregation results:\n"
        for group in result.groups:
            formatted += "-" * 40 + "\n"
            formatted += f"Group: {group.grouped_by.prop} = {group.grouped_by.value}\n"
            for prop_name, metrics in group.properties.items():
                formatted += f"Property: {prop_name}\n"
                for metric_name, value in metrics.__dict__.items():
                    if value is not None:
                        if metric_name == "top_occurrences":
                            formatted += f"  Most common values:\n"
                            for occurrence in value:
                                formatted += f"    - {occurrence.value} (count: {occurrence.count})\n"
                        else:
                            formatted += f"  {metric_name}: {value}\n"
            formatted += f"Group count: {group.total_count}\n"
        return formatted

    return str(result)
