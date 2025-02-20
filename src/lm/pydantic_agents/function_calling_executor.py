import weaviate.classes as wvc
from weaviate.collections import Collection
from weaviate.collections.classes.filters import _FilterByProperty
from typing import Any, Union

from src.models import (
    WeaviateQuery,
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation,
)

def _build_filter(
    f: Union[IntPropertyFilter, TextPropertyFilter, BooleanPropertyFilter]
) -> _FilterByProperty:
    """Build a Weaviate filter from a property filter."""
    operators = {
        "=": "equal",
        "!=": "not_equal",
        "<": "less_than",
        ">": "greater_than",
        "<=": "less_or_equal",
        ">=": "greater_or_equal",
        "LIKE": "like",
    }

    method_name = operators.get(f.operator)
    if not method_name:
        raise ValueError(f"Unsupported operator: {f.operator}")

    value = f.value
    if isinstance(f, BooleanPropertyFilter):
        value = bool(value)

    filter_prop = wvc.query.Filter.by_property(f.property_name)
    return getattr(filter_prop, method_name)(value)


def _build_numeric_metric(agg: IntAggregation) -> wvc.query.Metrics:
    """Build numeric metrics for aggregation."""
    metric = wvc.query.Metrics(agg.property_name)

    metric_map = {
        "MIN": lambda m: m.number(minimum=True),
        "MAX": lambda m: m.number(maximum=True),
        "MEAN": lambda m: m.number(mean=True),
        "SUM": lambda m: m.number(sum_=True),
    }

    return metric_map[agg.metrics](metric)


def _build_text_metric(agg: TextAggregation) -> wvc.query.Metrics:
    """Build text metrics for aggregation."""
    metric = wvc.query.Metrics(agg.property_name)

    if agg.metrics == "COUNT":
        return metric.count()
    elif agg.metrics == "TOP_OCCURRENCES":
        return metric.text(
            top_occurrences_count=True,
            top_occurrences_value=True,
        )
    return metric.count()  # default


def _build_boolean_metric(agg: BooleanAggregation) -> wvc.query.Metrics:
    """Build boolean metrics for aggregation."""
    metric = wvc.query.Metrics(agg.property_name)

    metric_map = {
        "TOTAL_TRUE": lambda m: m.boolean(total_true=True),
        "TOTAL_FALSE": lambda m: m.boolean(total_false=True),
        "PERCENTAGE_TRUE": lambda m: m.boolean(percentage_true=True),
        "PERCENTAGE_FALSE": lambda m: m.boolean(percentage_false=True),
    }

    return metric_map[agg.metrics](metric)


def _format_query_result(result: Any) -> str:
    """Format query results into a readable string."""

    # Handle QueryReturn objects (regular search/filter queries)
    if hasattr(result, "objects"):
        formatted = "Found objects:\n"
        for obj in result.objects:
            formatted += "-" * 40 + "\n"
            for key, value in obj.properties.items():
                formatted += f"{key}: {value}\n"
        if hasattr(result, "total_count"):
            formatted += f"\nTotal matching results: {result.total_count}\n"
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


def execute_weaviate_query(
    collection,
    query: WeaviateQuery,
    return_properties: list[str] | None = None,
) -> str:
    # Build filters if any exist
    filters = None
    if query.integer_property_filter:
        filters = _build_filter(query.integer_property_filter)
    elif query.text_property_filter:
        filters = _build_filter(query.text_property_filter)
    elif query.boolean_property_filter:
        filters = _build_filter(query.boolean_property_filter)

    # Handle aggregations if they exist
    if any([
        query.integer_property_aggregation,
        query.text_property_aggregation,
        query.boolean_property_aggregation,
    ]):
        metrics = []
        if query.integer_property_aggregation:
            metrics.append(_build_numeric_metric(query.integer_property_aggregation))
        if query.text_property_aggregation:
            metrics.append(_build_text_metric(query.text_property_aggregation))
        if query.boolean_property_aggregation:
            metrics.append(_build_boolean_metric(query.boolean_property_aggregation))

        group_by = None
        if query.groupby_property:
            group_by = wvc.aggregate.GroupByAggregate(prop=query.groupby_property)

        if query.search_query:
            result = collection.aggregate.near_text(
                query=query.search_query,
                object_limit=query.limit,
                total_count=query.total_count if query.total_count is not None else True,
                group_by=group_by,
                return_metrics=metrics,
                filters=wvc.query.Filter.all_of([filters]) if filters else None,
            )
        else:
            result = collection.aggregate.over_all(
                total_count=query.total_count if query.total_count is not None else True,
                group_by=group_by,
                return_metrics=metrics,
                filters=wvc.query.Filter.all_of([filters]) if filters else None,
            )
    else:
        # Handle regular queries - use hybrid only when there's a search query
        if query.search_query:
            result = collection.query.hybrid(
                query=query.search_query,
                filters=wvc.query.Filter.all_of([filters]) if filters else None,
                limit=query.limit,
                return_properties=return_properties,
            )
        else:
            # Use fetch() for filter-only queries
            result = collection.query.fetch_objects(
                filters=wvc.query.Filter.all_of([filters]) if filters else None,
                limit=query.limit,
                return_properties=return_properties,
            )

    return _format_query_result(result)


def query_collection(weaviate_client, query: WeaviateQuery) -> str:
    """Query Weaviate, Return Search Results or Aggregations."""
    collection = weaviate_client.collections.get(query.target_collection)
    return execute_weaviate_query(
        collection=collection,
        query=query,
        return_properties=None
    )