# Tie together the nodes and executors here
import asyncio
import time
from typing import Union, overload

from pydantic import BaseModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.result import Usage
from weaviate.collections import CollectionAsync
from weaviate.outputs.aggregate import AggregateReturn
from weaviate.outputs.query import QueryReturn
from colorama import Fore, Style

from src.lm.pydantic_agents.executors import aggregate as aggregate_executor
from src.lm.pydantic_agents.executors import search as search_executor
from src.lm.pydantic_agents.nodes import (
    AggregationAgentDeps,
    AggregationQuery,
    AggregationResult,
    EvaluateAgentDeps,
    EvaluateResult,
    QueryAgentDeps,
    QueryResult,
    SearchQuery,
    SearchRouterAgentDeps,
    SearchRouterResult,
    aggregation_agent,
    evaluate_agent,
    query_agent,
    search_router_agent,
)


class WeaviateSearchAgentSimpleResponse(BaseModel):
    original_query: str
    collection_names: list[str]
    searches: list[list[QueryResult]]
    aggregations: list[list[AggregationResult]]
    usage: Usage
    total_time: float
    search_answer: str | None
    aggregation_answer: str | None
    has_aggregation_answer: bool
    has_search_answer: bool
    is_partial_answer: bool
    missing_information: list[str]
    final_answer: str


class WeaviateSearchAgentSimple:

    def __init__(
        self,
        query: str,
        collections: list[CollectionAsync],
        schemas: dict[str, dict[str, dict[str, str | bool]]],
        tenant: str | None,
        max_limit: int = 20,
        collection_view_properties: list[str] | None = None,
    ):
        """Initialize the agent with the provided attributes."""
        print(f"{Fore.CYAN}Initializing WeaviateSearchAgentSimple...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Query: {query}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Collections: {[c.name for c in collections]}{Style.RESET_ALL}")
        
        self.query = query
        self.collections = collections
        self.tenant = tenant
        self.schemas = schemas
        self.max_limit = max_limit

        # TODO: right now this is a list of properties that can be viewed by the agent across
        # all collections, meaning if two collections have the same property name, it will
        # be included in the output, in future we should make this more fine-grained
        self.collection_view_properties = (
            list(set(collection_view_properties))
            if collection_view_properties
            else None
        )

        self.usage = Usage(
            request_tokens=0,
            requests=0,
            response_tokens=0,
            total_tokens=0,
        )
        self.searches: list[list[QueryResult]] = []
        self.aggregations: list[list[AggregationResult]] = []

        self.openai_model_name = "gpt-4o"
        print(f"{Fore.CYAN}Initialization complete{Style.RESET_ALL}")

    @overload
    @classmethod
    async def create(
        cls,
        query: str,
        collections: CollectionAsync,
        tenant: str | None,
        collection_view_properties: list[str] | None = None,
        limit: int = 20,
    ) -> "WeaviateSearchAgentSimple": ...

    @overload
    @classmethod
    async def create(
        cls,
        query: str,
        collections: list[CollectionAsync],
        tenant: str | None,
        collection_view_properties: list[str] | None = None,
        limit: int = 20,
    ) -> "WeaviateSearchAgentSimple": ...

    @classmethod
    async def create(
        cls,
        query: str,
        collections: Union[CollectionAsync, list[CollectionAsync]],
        tenant: str | None,
        collection_view_properties: Union[list[str], None] = None,
        limit: int = 20,
    ) -> "WeaviateSearchAgentSimple":
        """Factory method to create and initialize a WeaviateQueryAgentSimple instance."""
        print(f"{Fore.CYAN}Creating new WeaviateSearchAgentSimple instance...{Style.RESET_ALL}")
        
        # Convert single collection to list for unified processing
        collections_list = (
            [collections] if isinstance(collections, CollectionAsync) else collections
        )

        print(f"{Fore.GREEN}Building schemas for collections...{Style.RESET_ALL}")
        schemas = {
            collection.name: cls.get_collection_schemas(
                (await collection.config.get()).properties
            )
            for collection in collections_list
        }

        # TODO: potentially remove this as there is a difference between
        # what we want the agent to see at the end of the pipeline and what we want it to be able to filter on.
        if collection_view_properties:
            print(f"{Fore.GREEN}Filtering schemas based on view properties: {collection_view_properties}{Style.RESET_ALL}")
            for collection in collections_list:
                schemas[collection.name] = {
                    k: v
                    for k, v in schemas[collection.name].items()
                    if k in collection_view_properties
                }

        return cls(
            query, collections_list, schemas, tenant, limit, collection_view_properties
        )

    async def run(self, query: str) -> WeaviateSearchAgentSimpleResponse:
        print(f"\n{Fore.CYAN}Starting agent run with query: {query}{Style.RESET_ALL}")
        t0 = time.time()
        
        print(f"{Fore.GREEN}Running router node...{Style.RESET_ALL}")
        router_result = await self._run_router_node(query)
        print(f"{Fore.YELLOW}Router node response: {router_result}{Style.RESET_ALL}")
        searches = router_result.actions.searches
        aggregations = router_result.actions.aggregations
        print(f"{Fore.GREEN}Router returned {len(searches)} searches and {len(aggregations)} aggregations{Style.RESET_ALL}")

        print(f"{Fore.GREEN}Running concurrent nodes...{Style.RESET_ALL}")
        agg_node_results, search_node_results = await self._run_concurrent_nodes(
            aggregations, searches
        )
        print(f"{Fore.YELLOW}Aggregation node results: {agg_node_results}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Search node results: {search_node_results}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Node results received - Aggregations: {len(agg_node_results)}, Searches: {len(search_node_results)}{Style.RESET_ALL}")

        print(f"{Fore.GREEN}Running concurrent executors...{Style.RESET_ALL}")
        agg_executor_results, search_executor_results = (
            await self._run_concurrent_executors(
                agg_node_results, search_node_results, aggregations, searches
            )
        )
        print(f"{Fore.YELLOW}Aggregation executor results: {agg_executor_results}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Search executor results: {search_executor_results}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Executor results received{Style.RESET_ALL}")

        stringified_search_results = []
        for idx, search_result in enumerate(search_executor_results):
            print(f"{Fore.CYAN}Processing search result {idx+1}/{len(search_executor_results)}{Style.RESET_ALL}")
            stringified_result = self._stringify_search_result(search_result, searches[idx].query)
            print(f"{Fore.YELLOW}Stringified search result: {stringified_result}{Style.RESET_ALL}")
            stringified_search_results.append(stringified_result)

        stringified_agg_results = self._stringify_aggregation_results(
            agg_executor_results, [agg.query for agg in aggregations]
        )
        print(f"{Fore.YELLOW}Stringified aggregation results: {stringified_agg_results}{Style.RESET_ALL}")

        print(f"{Fore.GREEN}Running evaluate node...{Style.RESET_ALL}")
        evaluate_result = await self._run_evaluate_node(
            stringified_search_results,
            stringified_agg_results,
        )
        print(f"{Fore.YELLOW}Evaluate node response: {evaluate_result}{Style.RESET_ALL}")

        final_time = time.time() - t0
        print(f"{Fore.CYAN}Total execution time: {final_time:.2f} seconds{Style.RESET_ALL}")

        response = WeaviateSearchAgentSimpleResponse(
            original_query=self.query,
            collection_names=[c.name for c in self.collections],
            searches=self.searches,
            aggregations=self.aggregations,
            usage=self.usage,
            total_time=final_time,
            search_answer=evaluate_result.evaluation.search_answer,
            aggregation_answer=evaluate_result.evaluation.aggregation_answer,
            has_aggregation_answer=evaluate_result.evaluation.has_aggregation_answer,
            has_search_answer=evaluate_result.evaluation.has_search_answer,
            is_partial_answer=evaluate_result.evaluation.is_partial_answer,
            missing_information=evaluate_result.evaluation.missing_information,
            final_answer=self.construct_final_answer(
                evaluate_result.evaluation.search_answer,
                evaluate_result.evaluation.aggregation_answer,
            ),
        )

        print(f"{Fore.CYAN}Agent run completed successfully{Style.RESET_ALL}")
        return response

    async def _run_router_node(self, query: str) -> SearchRouterResult:
        """
        Runs the search router on the initial query and returns a template of
        the proposed aggregations and searches that should be executed in order
        to answer the query.
        """
        print(f"{Fore.GREEN}Router node processing query: {query}{Style.RESET_ALL}")
        router_deps = SearchRouterAgentDeps(collection_schemas=self.schemas)
        openai_model = OpenAIModel(model_name=self.openai_model_name)
        result = await search_router_agent.run(
            query, deps=router_deps, model=openai_model
        )
        self._update_usage(result.usage())
        print(f"{Fore.GREEN}Router node completed{Style.RESET_ALL}")
        return result.data

    async def _run_aggregation_node(
        self, aggregation_queries: list[AggregationQuery]
    ) -> list[AggregationResult]:
        """
        Run proposed aggregations through the aggregation agent and
        returns template of aggregations to be executed
        """
        print(f"{Fore.GREEN}Running aggregation node with {len(aggregation_queries)} queries{Style.RESET_ALL}")
        openai_model = OpenAIModel(model_name=self.openai_model_name)
        aggregations = await asyncio.gather(
            *[
                aggregation_agent.run(
                    agg_query.query,
                    deps=AggregationAgentDeps(
                        collection_schema=self.schemas[agg_query.collection.name]
                    ),
                    model=openai_model,
                )
                for agg_query in aggregation_queries
            ]
        )
        [self._update_usage(agg.usage()) for agg in aggregations]
        self.aggregations.append([agg.data for agg in aggregations])
        print(f"{Fore.GREEN}Aggregation node completed{Style.RESET_ALL}")
        return [agg.data for agg in aggregations]

    async def _run_query_node(
        self, search_queries: list[SearchQuery]
    ) -> list[QueryResult]:
        """
        Run proposed searches through the search query agent and
        returns template of queries to be executed
        """
        print(f"{Fore.GREEN}Running query node with {len(search_queries)} queries{Style.RESET_ALL}")
        openai_model = OpenAIModel(model_name=self.openai_model_name)
        search_results = await asyncio.gather(
            *[
                query_agent.run(
                    search_query.query,
                    deps=QueryAgentDeps(
                        collection_schema=self.schemas[search_query.collection.name]
                    ),
                    model=openai_model,
                )
                for search_query in search_queries
            ]
        )
        [self._update_usage(search_result.usage()) for search_result in search_results]
        self.searches.append([search_result.data for search_result in search_results])
        print(f"{Fore.GREEN}Query node completed{Style.RESET_ALL}")
        return [search_result.data for search_result in search_results]

    async def _run_evaluate_node(
        self,
        search_results: list[str],
        aggregation_results: list[str],
    ) -> EvaluateResult:
        """
        Run results of searches and aggregations through the evaluation agent and
        returns a data model with the final answer(s) and metadata about the final
        answer(s)
        """
        print(f"{Fore.GREEN}Running evaluate node{Style.RESET_ALL}")
        openai_model = OpenAIModel(model_name=self.openai_model_name)
        evaluate_deps = EvaluateAgentDeps(
            original_query=self.query,
            search_results=search_results,
            aggregation_results=aggregation_results,
        )

        result = await evaluate_agent.run(
            "Evaluate the search and aggregation results and provide a detailed answer to the original query if possible",
            deps=evaluate_deps,
            model=openai_model,
        )
        self._update_usage(result.usage())
        print(f"{Fore.GREEN}Evaluate node completed{Style.RESET_ALL}")
        return result.data

    async def _run_aggregation_executor(
        self,
        aggregation_results: list[AggregationResult],
        aggregation_queries: list[AggregationQuery],
    ) -> list[AggregateReturn]:
        """Executes the template of aggregations using the executor."""
        print(f"{Fore.GREEN}Running aggregation executor with {len(aggregation_results)} results{Style.RESET_ALL}")
        collection_map = {c.name: c for c in self.collections}

        results = await asyncio.gather(
            *[
                aggregate_executor(
                    collection=collection_map[query.collection.name],
                    aggregation_result=result,
                )
                for result, query in zip(aggregation_results, aggregation_queries)
            ]
        )

        print(f"{Fore.GREEN}Aggregation executor completed{Style.RESET_ALL}")
        return results

    async def _run_query_executor(
        self,
        query_results: list[QueryResult],
        search_queries: list[SearchQuery],
    ) -> list[list[QueryReturn]]:
        """Executes the template of queries using the executor."""
        print(f"{Fore.GREEN}Running query executor with {len(query_results)} results{Style.RESET_ALL}")
        collection_map = {c.name: c for c in self.collections}
        limit_per_query = -(-self.max_limit // len(search_queries))

        results = await asyncio.gather(
            *[
                search_executor(
                    collection=collection_map[query.collection.name],
                    query_result=result,
                    limit=limit_per_query,
                    return_properties=self.collection_view_properties,
                )
                for result, query in zip(query_results, search_queries)
            ]
        )

        print(f"{Fore.GREEN}Query executor completed{Style.RESET_ALL}")
        return results

    async def _run_concurrent_nodes(
        self,
        aggregations: list[AggregationQuery],
        searches: list[SearchQuery],
    ) -> tuple[list[AggregationResult], list[QueryResult]]:
        """Run aggregation and query nodes concurrently if there are tasks to run."""
        print(f"{Fore.GREEN}Setting up concurrent nodes - Aggregations: {len(aggregations)}, Searches: {len(searches)}{Style.RESET_ALL}")
        tasks: list[asyncio.Task[list[AggregationResult] | list[QueryResult]]] = []

        if len(aggregations) > 0:
            tasks.append(asyncio.create_task(self._run_aggregation_node(aggregations)))
        if len(searches) > 0:
            tasks.append(asyncio.create_task(self._run_query_node(searches)))

        # Initialize empty results
        agg_results: list[AggregationResult] = []
        search_results: list[QueryResult] = []

        if tasks:
            print(f"{Fore.GREEN}Awaiting {len(tasks)} concurrent tasks{Style.RESET_ALL}")
            results = await asyncio.gather(*tasks)

            # Unpack results based on which tasks were created
            if len(aggregations) > 0 and len(searches) > 0:
                agg_results, search_results = results[0], results[1]  # type: ignore
            elif len(aggregations) > 0:
                [agg_results] = results  # type: ignore
            elif len(searches) > 0:
                [search_results] = results  # type: ignore

        print(f"{Fore.GREEN}Concurrent nodes completed{Style.RESET_ALL}")
        return agg_results, search_results

    async def _run_concurrent_executors(
        self,
        agg_results: list[AggregationResult],
        search_results: list[QueryResult],
        aggregations: list[AggregationQuery],
        searches: list[SearchQuery],
    ) -> tuple[list[AggregateReturn], list[list[QueryReturn]]]:
        """Run aggregation and search executors concurrently if there are results."""
        print(f"{Fore.GREEN}Setting up concurrent executors{Style.RESET_ALL}")
        tasks: list[asyncio.Task[list[AggregateReturn] | list[list[QueryReturn]]]] = []

        if agg_results:
            tasks.append(
                asyncio.create_task(
                    self._run_aggregation_executor(agg_results, aggregations)
                )
            )
        if search_results:
            tasks.append(
                asyncio.create_task(self._run_query_executor(search_results, searches))
            )

        # Initialize empty results
        agg_executor_results: list[AggregateReturn] = []
        search_executor_results: list[list[QueryReturn]] = []

        if tasks:
            print(f"{Fore.GREEN}Awaiting {len(tasks)} concurrent executor tasks{Style.RESET_ALL}")
            results = await asyncio.gather(*tasks)

            # Unpack results based on which tasks were created
            if len(agg_results) > 0 and len(search_results) > 0:
                agg_executor_results, search_executor_results = results[0], results[1]  # type: ignore
            elif len(agg_results) > 0:
                [agg_executor_results] = results  # type: ignore
            elif len(search_results) > 0:
                [search_executor_results] = results  # type: ignore

        print(f"{Fore.GREEN}Concurrent executors completed{Style.RESET_ALL}")
        return agg_executor_results, search_executor_results

    def _stringify_search_result(self, results: list[QueryReturn], query: str) -> str:
        """Stringify the results of the search executor."""
        print(f"{Fore.GREEN}Stringifying search results for query: {query}{Style.RESET_ALL}")
        stringified_response = ""
        for idx, result in enumerate(results):
            stringified_response += f"Search Result {idx+1} (Query: {query}):\n"
            for prop in result.objects:
                for prop_name in prop.properties:
                    stringified_response += (
                        f"{prop_name}: {prop.properties[prop_name]}\n"
                    )
            stringified_response += "\n"
        return stringified_response

    def _stringify_aggregation_results(
        self, results: list[AggregateReturn], queries: list[str]
    ) -> list[str]:
        """Stringify the results of the aggregation executor."""
        print(f"{Fore.GREEN}Stringifying {len(results)} aggregation results{Style.RESET_ALL}")
        stringified_responses = []
        
        for idx, (result, query) in enumerate(zip(results, queries)):
            response = f"Aggregation Result {idx+1} (Query: {query}):\n"
            
            # Handle grouped results (AggregateGroupByReturn)
            if hasattr(result, 'groups'):
                response += f"Found {len(result.groups)} groups:\n"
                for group in result.groups:
                    response += f"\nGroup: {group.grouped_by.prop} = {group.grouped_by.value}\n"
                    if hasattr(group, 'total_count'):
                        response += f"Total Count: {group.total_count}\n"
                    
                    if hasattr(group, 'properties'):
                        for prop_name, metrics in group.properties.items():
                            response += f"\n{prop_name} metrics:\n"
                            
                            # Handle text metrics with top occurrences
                            if hasattr(metrics, 'top_occurrences') and metrics.top_occurrences:
                                response += "Top occurrences:\n"
                                for occurrence in metrics.top_occurrences:
                                    response += f"  {occurrence.value}: {occurrence.count}\n"
                            
                            # Handle numeric metrics
                            if hasattr(metrics, 'count') and metrics.count is not None:
                                response += f"  count: {metrics.count}\n"
                            if hasattr(metrics, 'minimum') and metrics.minimum is not None:
                                response += f"  minimum: {metrics.minimum}\n"
                            if hasattr(metrics, 'maximum') and metrics.maximum is not None:
                                response += f"  maximum: {metrics.maximum}\n"
                            if hasattr(metrics, 'mean') and metrics.mean is not None:
                                response += f"  mean: {metrics.mean:.2f}\n"
                            if hasattr(metrics, 'sum_') and metrics.sum_ is not None:
                                response += f"  sum: {metrics.sum_}\n"
            
            # Handle non-grouped results (AggregateReturn)
            elif hasattr(result, 'properties'):
                for prop_name, metrics in result.properties.items():
                    response += f"\n{prop_name} metrics:\n"
                    if hasattr(metrics, 'count') and metrics.count is not None:
                        response += f"  count: {metrics.count}\n"
                    if hasattr(metrics, 'mean') and metrics.mean is not None:
                        response += f"  mean: {metrics.mean:.2f}\n"
                    if hasattr(metrics, 'maximum') and metrics.maximum is not None:
                        response += f"  maximum: {metrics.maximum}\n"
                    if hasattr(metrics, 'minimum') and metrics.minimum is not None:
                        response += f"  minimum: {metrics.minimum}\n"
                    if hasattr(metrics, 'sum_') and metrics.sum_ is not None:
                        response += f"  sum: {metrics.sum_}\n"
                
                if hasattr(result, 'total_count'):
                    response += f"\nTotal Count: {result.total_count}\n"
            
            stringified_responses.append(response)
            
        return stringified_responses

    def _update_usage(self, usage: Usage):
        """Updates the usage of the agent."""
        self.usage.request_tokens = (self.usage.request_tokens or 0) + (
            usage.request_tokens or 0
        )
        self.usage.requests += 1
        self.usage.response_tokens = (self.usage.response_tokens or 0) + (
            usage.response_tokens or 0
        )
        self.usage.total_tokens = (self.usage.total_tokens or 0) + (
            usage.total_tokens or 0
        )
        print(f"{Fore.CYAN}Updated usage - Total tokens: {self.usage.total_tokens}, Requests: {self.usage.requests}{Style.RESET_ALL}")

    @staticmethod
    def get_collection_schemas(properties_list) -> dict[str, dict[str, str | bool]]:
        """Convert collection properties into a detailed mapping of property metadata."""
        return {
            prop.name: {
                "type": prop.data_type.value,
                "description": prop.description,
                "searchable": prop.index_searchable,
                "filterable": prop.index_filterable,
            }
            for prop in properties_list
        }

    @staticmethod
    def construct_final_answer(
        search_answer: str | None, aggregation_answer: str | None
    ) -> str:
        """Construct the final answer from the search and aggregation answers."""
        if search_answer and aggregation_answer:
            return f"Aggregation Answer: {aggregation_answer}\nSearch Answer: {search_answer}"
        return search_answer or aggregation_answer or ""