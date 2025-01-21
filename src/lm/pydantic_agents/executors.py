# Weaviate Query Executor
import asyncio
from typing import List, Union, Any, Optional

import weaviate.classes as wc
from pydantic import BaseModel
from weaviate.collections import CollectionAsync
from weaviate.collections.classes.aggregate import (
    _MetricsBoolean,
    _MetricsInteger,
    _MetricsNumber,
    _MetricsText,
    AggregateInteger,
    AggregateNumber
)
from weaviate.collections.classes.filters import _FilterByProperty, _Filters
from weaviate.outputs.query import QueryReturn
from weaviate.outputs.aggregate import AggregateReturn
from src.lm.pydantic_agents.nodes import (
    AggregationResult,
    BooleanPropertyAggregation,
    BooleanPropertyFilter,
    ComparisonOperator,
    IntegerPropertyAggregation,
    IntegerPropertyFilter,
    QueryResult,
    TextPropertyAggregation,
    TextPropertyFilter,
)

PropertyFilter = Union[IntegerPropertyFilter, TextPropertyFilter, BooleanPropertyFilter]
Aggregation = Union[
    BooleanPropertyAggregation, IntegerPropertyAggregation, TextPropertyAggregation
]


class SearchArgs(BaseModel):
    query: str
    filters: List[PropertyFilter]


class AggregationArgs(BaseModel):
    total_count: bool
    group_by: Optional[wc.aggregate.GroupByAggregate]
    return_metrics: list[
        _MetricsBoolean | _MetricsInteger | _MetricsNumber | _MetricsText
    ]


async def search(
    collection: CollectionAsync,
    query_result: QueryResult,
    limit: int,
    return_properties: list[str] | None = None,
) -> list[QueryReturn]:
    """Execute search queries with optional filters on a Weaviate collection."""
    results = []

    # Create search tasks for each query
    search_tasks = []
    for i, query in enumerate(query_result.queries):
        filters = query_result.filters[i] if i < len(query_result.filters) else []

        search_args = SearchArgs(query=query, filters=filters)
        w_filters = _build_filters(search_args.filters) if search_args.filters else None

        search_tasks.append(
            collection.query.hybrid(
                query=search_args.query,
                filters=wc.query.Filter.all_of(w_filters) if w_filters else None,
                limit=limit,
                return_properties=return_properties,
            )
        )

    results = await asyncio.gather(*search_tasks)
    return results


def _build_filters(filters: List[PropertyFilter]) -> List[_Filters] | None:
    """Build Weaviate filters from PropertyFilter objects."""
    if not filters:
        return None

    def create_filter(f: PropertyFilter) -> _FilterByProperty | None:
        operators = {
            ComparisonOperator.EQUALS: "equal",
            ComparisonOperator.NOT_EQUALS: "not_equal",
            ComparisonOperator.LESS_THAN: "less_than",
            ComparisonOperator.GREATER_THAN: "greater_than",
            ComparisonOperator.LESS_EQUAL: "less_or_equal",
            ComparisonOperator.GREATER_EQUAL: "greater_or_equal",
            ComparisonOperator.LIKE: "like",
        }

        method_name = operators.get(f.operator)
        if method_name:
            value = f.value
            if isinstance(f, BooleanPropertyFilter):
                value = bool(value)

            filter_prop = wc.query.Filter.by_property(f.property_name)
            return getattr(filter_prop, method_name)(value)
        return None

    return [create_filter(f) for f in filters if create_filter(f) is not None]  # type: ignore

async def process_results(aggregation_results: List[AggregateReturn], search_results: List[QueryReturn]):
    """Process both aggregation and search results."""
    print(f"\nReceived {len(search_results)} search results and {len(aggregation_results)} aggregation results")

    # Process search results
    if search_results:
        for i, result in enumerate(search_results, 1):
            print(f"\nSearch Result Set {i}:")
            print(f"Number of objects in result set: {len(result.objects)}")
            for item in result.objects:
                print(f"\nObject properties: {list(item.properties.keys())}")
                for prop, value in item.properties.items():
                    print(f"{prop}: {value}")
                print("---")
    else:
        print("No search results to process")

    # Process aggregation results
    if aggregation_results:
        print(f"\nAggregation Results (count: {len(aggregation_results)}):")
        for idx, agg_result in enumerate(aggregation_results):
            print(f"\nProcessing aggregation result {idx + 1}")
            print(f"Result type: {type(agg_result)}")
            print(f"Available attributes: {dir(agg_result)}")
            
            try:
                # Handle grouped results (AggregateGroupByReturn)
                if hasattr(agg_result, 'groups'):
                    print(f"Found grouped result with {len(agg_result.groups)} groups")
                    for group_idx, group in enumerate(agg_result.groups):
                        print(f"\nProcessing group {group_idx + 1}")
                        print(f"Group attributes: {dir(group)}")
                        print(f"Group: {group.grouped_by.prop} = {group.grouped_by.value}")
                        
                        if hasattr(group, 'total_count'):
                            print(f"Total Count: {group.total_count}")
                        
                        if hasattr(group, 'properties'):
                            print(f"Properties in group: {list(group.properties.keys())}")
                            for prop_name, metrics in group.properties.items():
                                print(f"\n{prop_name} metrics (type: {type(metrics)}):")
                                print(f"Metrics attributes: {dir(metrics)}")
                                
                                # Handle AggregateText specifically
                                if hasattr(metrics, 'top_occurrences') and metrics.top_occurrences:
                                    print("  Top occurrences:")
                                    for occurrence in metrics.top_occurrences:
                                        print(f"    {occurrence.value}: {occurrence.count}")
                                
                                # Handle numeric metrics
                                if isinstance(metrics, (AggregateInteger, AggregateNumber)):
                                    print(f"  Available numeric metrics: count={metrics.count}, "
                                          f"min={metrics.minimum}, max={metrics.maximum}, "
                                          f"mean={metrics.mean}, sum={metrics.sum_}")
                                    if metrics.count is not None:
                                        print(f"  count: {metrics.count}")
                                    if metrics.minimum is not None:
                                        print(f"  minimum: {metrics.minimum}")
                                    if metrics.maximum is not None:
                                        print(f"  maximum: {metrics.maximum}")
                                    if metrics.mean is not None:
                                        print(f"  mean: {metrics.mean:.2f}")
                                    if metrics.sum_ is not None:
                                        print(f"  sum: {metrics.sum_}")
                
                # Handle non-grouped results (AggregateReturn)
                elif hasattr(agg_result, 'properties'):
                    print(f"Found non-grouped result with properties: {list(agg_result.properties.keys())}")
                    for prop_name, metrics in agg_result.properties.items():
                        print(f"\n{prop_name} metrics (type: {type(metrics)}):")
                        print(f"Metrics attributes: {dir(metrics)}")
                        if isinstance(metrics, (AggregateInteger, AggregateNumber)):
                            print(f"  Available numeric metrics: count={metrics.count}, "
                                  f"min={metrics.minimum}, max={metrics.maximum}, "
                                  f"mean={metrics.mean}, sum={metrics.sum_}")
                            if metrics.count is not None:
                                print(f"  count: {metrics.count}")
                            if metrics.mean is not None:
                                print(f"  mean: {metrics.mean:.2f}")
                            if metrics.maximum is not None:
                                print(f"  maximum: {metrics.maximum}")
                            if metrics.minimum is not None:
                                print(f"  minimum: {metrics.minimum}")
                            if metrics.sum_ is not None:
                                print(f"  sum: {metrics.sum_}")
                else:
                    print(f"Warning: Unexpected aggregation result type: {type(agg_result)}")
                    print(f"Available attributes: {dir(agg_result)}")
                    
                if hasattr(agg_result, 'total_count'):
                    print(f"\nTotal Count: {agg_result.total_count}")
                    
            except Exception as e:
                print(f"Error processing aggregation result: {str(e)}")
                print(f"Result type: {type(agg_result)}")
                print(f"Error details: {repr(e)}")
                print(f"Available attributes: {dir(agg_result)}")
                raise  # Re-raise the exception to see the full stack trace


async def aggregate(
    collection: CollectionAsync, 
    aggregation_result: AggregationResult
) -> AggregateReturn:
    """Execute aggregation query and return raw results."""
    try:
        agg_args = AggregationArgs(
            total_count=True,
            group_by=(
                wc.aggregate.GroupByAggregate(prop=aggregation_result.groupby_property)
                if aggregation_result.groupby_property
                else None
            ),
            return_metrics=_build_return_metrics(aggregation_result.aggregations),
        )

        if aggregation_result.search_query:
            result = await collection.aggregate.near_text(
                query=aggregation_result.search_query,
                object_limit=1000,
                total_count=agg_args.total_count,
                group_by=agg_args.group_by,
                return_metrics=agg_args.return_metrics,
            )
        else:
            result = await collection.aggregate.over_all(
                total_count=agg_args.total_count,
                group_by=agg_args.group_by,
                return_metrics=agg_args.return_metrics,
            )
        
        return result

    except Exception as e:
        print(f"Error during aggregation: {str(e)}")
        raise


def _build_return_metrics(
    aggregations: list[Aggregation],
) -> list[_MetricsBoolean | _MetricsInteger | _MetricsNumber | _MetricsText]:
    """Build return metrics for aggregation queries."""
    metrics_list: list[
        _MetricsBoolean | _MetricsNumber | _MetricsText | _MetricsInteger
    ] = []

    for agg in aggregations:
        if hasattr(agg, "property_name") and hasattr(agg, "metrics"):
            if isinstance(agg, BooleanPropertyAggregation):
                metrics_list.append(
                    wc.query.Metrics(agg.property_name).boolean(
                        **{agg.metrics.value.lower(): True}
                    )
                )
            elif isinstance(agg, IntegerPropertyAggregation):
                metric_name = agg.metrics.value.lower()
                if metric_name == "sum":
                    metric_name = "sum_"
                metrics_list.append(
                    wc.query.Metrics(agg.property_name).integer(
                        **{metric_name: True}
                    )
                )
            elif isinstance(agg, TextPropertyAggregation):
                if agg.metrics.lower() == "top_occurrences":
                    metrics_list.append(
                        wc.query.Metrics(agg.property_name).text(
                            top_occurrences_count=True,
                            top_occurrences_value=True
                        )
                    )
                else:
                    metrics_list.append(
                        wc.query.Metrics(agg.property_name).text(
                            **{agg.metrics.value.lower(): True}
                        )
                    )

    return metrics_list


async def main():
    """Test AggregateGroupByReturn object parsing."""
    from dataclasses import dataclass
    
    @dataclass
    class GroupedBy:
        prop: str
        value: str
        
    @dataclass 
    class AggregateInteger:
        count: int
        maximum: None
        mean: None
        median: None
        minimum: None
        mode: None
        sum_: None
        
    @dataclass
    class AggregateGroup:
        grouped_by: GroupedBy
        properties: dict
        total_count: int
        
    @dataclass
    class AggregateGroupByReturn:
        groups: list
    
    # Create test object
    test_results = [
        AggregateGroupByReturn(groups=[
            AggregateGroup(
                grouped_by=GroupedBy(prop='openNow', value='true'),
                properties={'name': AggregateInteger(count=13, maximum=None, mean=None, median=None, minimum=None, mode=None, sum_=None)},
                total_count=13
            )
        ])
    ]
    
    # Process results
    await process_results(test_results, [])


if __name__ == "__main__":
    asyncio.run(main())