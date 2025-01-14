# Weaviate Query Executor
# search
import asyncio
from typing import List, Union

import weaviate.classes as wc
from pydantic import BaseModel
from weaviate.collections import CollectionAsync
from weaviate.collections.classes.aggregate import (
    _MetricsBoolean,
    _MetricsInteger,
    _MetricsNumber,
    _MetricsText,
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


class SearchArgs(BaseModel):
    query: str
    filters: List[PropertyFilter]


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


async def main():
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
        collection = client.collections.get("courses")

        schema = {
            "properties": {
                "currentlyEnrolling": "boolean",
                "courseTitle": "string",
                "courseDescription": "string",
                "courseDuration": "number",
            }
        }

        query_agent_deps = QueryAgentDeps(collection_schema=schema)

        query_result = await query_agent.run(
            "Describe the course where the course title is like Quantum Computing Fundamentals and are currently not enrolling",
            deps=query_agent_deps,
        )

        print(query_result.data)

        # Connect the client before searching
        await client.connect()

        results = await search(collection, query_result.data)
        print(results)

    finally:
        await client.close()

Aggregation = Union[
    BooleanPropertyAggregation, IntegerPropertyAggregation, TextPropertyAggregation
]


class AggregationArgs(BaseModel):
    total_count: bool
    group_by: wc.aggregate.GroupByAggregate | None
    return_metrics: list[
        _MetricsBoolean | _MetricsInteger | _MetricsNumber | _MetricsText
    ]


async def aggregate(
    collection: CollectionAsync, aggregation_result: AggregationResult
) -> AggregateReturn:
    agg_args = AggregationArgs(
        total_count=True,
        group_by=(
            wc.aggregate.GroupByAggregate(prop=aggregation_result.groupby_property)
            if aggregation_result.groupby_property
            else None
        ),
        return_metrics=_build_return_metrics(aggregation_result.aggregations),
    )

    # TODO: fix mypy errors for group_by and return_metrics, check if issue lies in client
    if aggregation_result.search_query:
        return await collection.aggregate.near_text(
            query=aggregation_result.search_query,
            object_limit=1000,
            total_count=agg_args.total_count,
            group_by=agg_args.group_by,  # type: ignore
            return_metrics=agg_args.return_metrics,  # type: ignore
        )
    else:
        return await collection.aggregate.over_all(
            total_count=agg_args.total_count,
            group_by=agg_args.group_by,  # type: ignore
            return_metrics=agg_args.return_metrics,  # type: ignore
        )


def _build_return_metrics(
    aggregations: list[Aggregation],
) -> list[_MetricsBoolean | _MetricsInteger | _MetricsNumber | _MetricsText]:
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
                continue
            elif isinstance(agg, IntegerPropertyAggregation):
                metrics_list.append(
                    wc.query.Metrics(agg.property_name).integer(
                        **{agg.metrics.value.lower(): True}
                    )
                )
                continue
            elif isinstance(agg, TextPropertyAggregation):
                metrics_list.append(
                    wc.query.Metrics(agg.property_name).text(
                        **{agg.metrics.value.lower(): True}
                    )
                )
                continue
    return metrics_list