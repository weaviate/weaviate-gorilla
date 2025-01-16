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
    # Process search results
    if search_results:
        for i, result in enumerate(search_results, 1):
            print(f"\nSearch Result Set {i}:")
            for item in result.objects:
                print(f"Menu Item: {item.properties['menuItem']}")
                print(f"Price: ${item.properties['price']:.2f}")
                print(f"Vegetarian: {item.properties['isVegetarian']}")
                print("---")

    # Process aggregation results
    if aggregation_results:
        print("\nAggregation Results:")
        for agg_result in aggregation_results:
            try:
                # Handle AggregateGroupByReturn object
                if hasattr(agg_result, 'groups') and agg_result.groups:  # Check if groups exist and is not empty
                    for group in agg_result.groups:
                        print(f"\nGroup: {group.grouped_by.prop} = {group.grouped_by.value}")
                        print(f"Count: {group.total_count}")
                        
                        for prop_name, metrics in group.properties.items():
                            print(f"{prop_name} metrics:")
                            if isinstance(metrics, (AggregateInteger, AggregateNumber)):
                                if metrics.mean is not None:
                                    print(f"  mean: {metrics.mean:.2f}")
                                if metrics.maximum is not None:
                                    print(f"  maximum: {metrics.maximum}")
                                if metrics.minimum is not None:
                                    print(f"  minimum: {metrics.minimum}")
                                if metrics.count is not None:
                                    print(f"  count: {metrics.count}")
                                if metrics.sum_ is not None:
                                    print(f"  sum: {metrics.sum_}")
                            else:
                                # Convert metrics object to dictionary, filtering None values
                                metrics_dict = {k: v for k, v in vars(metrics).items() if not k.startswith('_') and v is not None}
                                for metric_name, value in metrics_dict.items():
                                    print(f"  {metric_name}: {value}")
                
                # Handle AggregateReturn object
                if hasattr(agg_result, 'properties'):
                    for prop_name, metrics in agg_result.properties.items():
                        print(f"\n{prop_name} metrics:")
                        if isinstance(metrics, (AggregateInteger, AggregateNumber)):
                            if metrics.mean is not None:
                                print(f"  mean: {metrics.mean:.2f}")
                            if metrics.maximum is not None:
                                print(f"  maximum: {metrics.maximum}")
                            if metrics.minimum is not None:
                                print(f"  minimum: {metrics.minimum}")
                            if metrics.count is not None:
                                print(f"  count: {metrics.count}")
                            if metrics.sum_ is not None:
                                print(f"  sum: {metrics.sum_}")
                        else:
                            metrics_dict = {k: v for k, v in vars(metrics).items() if not k.startswith('_') and v is not None}
                            for metric_name, value in metrics_dict.items():
                                print(f"  {metric_name}: {value}")

                if hasattr(agg_result, 'total_count'):
                    print(f"\nTotal Count: {agg_result.total_count}")
                
            except Exception as e:
                print(f"Error processing aggregation result: {str(e)}")


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
                metrics_list.append(
                    wc.query.Metrics(agg.property_name).integer(
                        **{agg.metrics.value.lower(): True}
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
    """Example usage of the query executor."""
    import os
    import weaviate
    from weaviate.classes.init import Auth
    from coordinator.src.agents.nodes.query import QueryAgentDeps, query_agent

    client = weaviate.use_async_with_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
        headers={"X-Openai-Api-Key": os.getenv("OPENAI_APIKEY")},
    )

    try:
        collection = client.collections.get("Menus")

        # Example schema for menu items
        schema = {
            "properties": {
                "menuItem": "string",
                "itemDescription": "string",
                "price": "number",
                "isVegetarian": "boolean"
            }
        }

        query_agent_deps = QueryAgentDeps(collection_schema=schema)

        # Example query
        query_result = await query_agent.run(
            "Find vegetarian menu items under $20",
            deps=query_agent_deps,
        )

        # Connect the client before searching
        await client.connect()

        # Execute search
        search_results = await search(collection, query_result.data, limit=10)
        
        # Execute aggregation
        agg_results = []
        if hasattr(query_result.data, 'aggregations'):
            for agg in query_result.data.aggregations:
                agg_result = await aggregate(collection, agg)
                agg_results.append(agg_result)

        # Process and display results
        await process_results(agg_results, search_results)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())