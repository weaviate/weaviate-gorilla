# Models
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext
from typing_extensions import Literal

RETRIES = 3

# Router Models
class Collection(BaseModel):
    """A collection that can be searched or created."""
    name: str = Field(description="The name of the collection")

class SearchQuery(BaseModel):
    """A search query that can be performed on a collection."""
    query: str = Field(
        description="The part of the original query reframed to the part that is being searched for"
    )
    collection: Collection = Field(description="The collection to perform the query on")

class AggregationQuery(BaseModel):
    """An aggregation query that can be performed on a collection."""
    query: str = Field(
        description="The part of the original query that refers to the aggregation"
    )
    collection: Collection = Field(
        description="The collection to perform the aggregation on"
    )

class SearchActions(BaseModel):
    """Actions that can be performed during a search operation."""
    searches: List[SearchQuery] = Field(
        description="Collections to search through for finding or matching specific items"
    )
    aggregations: List[AggregationQuery] = Field(
        description="Collections to create and aggregate statistics from"
    )

class SearchRouterResult(BaseModel):
    """The final routing decision about what search actions to take."""
    actions: SearchActions = Field(
        description="The search and aggregation actions to perform"
    )

# Query Models
class ComparisonOperator(str, Enum):
    EQUALS = "="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    NOT_EQUALS = "!="
    LIKE = "LIKE"

class IntegerPropertyFilter(BaseModel):
    """Filter numeric properties using comparison operators."""
    property_name: str
    operator: ComparisonOperator
    value: float

class TextPropertyFilter(BaseModel):
    """Filter text properties using equality or LIKE operators"""
    property_name: str
    operator: ComparisonOperator
    value: str

class BooleanPropertyFilter(BaseModel):
    """Filter boolean properties using equality operators"""
    property_name: str
    operator: ComparisonOperator
    value: bool

class QueryResult(BaseModel):
    """
    The queries and respective filters to be run on a vector database collection.

    They should be based on the original user query.
    But can be decomposed into multiple queries if the user query is too complex.

    It is important that if the original user query cannot be return optimal results with
    one query, then it should be decomposed into multiple queries with a corresponding
    set of filters.
    """
    queries: list[str] = Field(description="The queries to run on the collection")
    filters: list[
        list[Union[BooleanPropertyFilter, IntegerPropertyFilter, TextPropertyFilter]]
    ] = Field(
        default=[],
        description="List of filter lists, where each inner list contains filters for the corresponding query",
    )
    filter_operators: Literal["AND", "OR"] = Field(
        default="AND",
        description="The logical operator to use when combining filters",
    )

# Aggregation Models
class NumericMetrics(str, Enum):
    COUNT = "COUNT"
    MAX = "MAXIMUM"
    MEAN = "MEAN"
    MEDIAN = "MEDIAN"
    MIN = "MINIMUM"
    MODE = "MODE"
    SUM = "SUM"
    TYPE = "TYPE"

class TextMetrics(str, Enum):
    COUNT = "COUNT"
    TYPE = "TYPE"
    TOP_OCCURRENCES = "TOP_OCCURRENCES"

class BooleanMetrics(str, Enum):
    COUNT = "COUNT"
    TYPE = "TYPE"
    TOTAL_TRUE = "TOTAL_TRUE"
    TOTAL_FALSE = "TOTAL_FALSE"
    PERCENTAGE_TRUE = "PERCENTAGE_TRUE"
    PERCENTAGE_FALSE = "PERCENTAGE_FALSE"

class IntegerPropertyAggregation(BaseModel):
    """Aggregate numeric properties using statistical functions"""
    property_name: str
    metrics: NumericMetrics

class TextPropertyAggregation(BaseModel):
    """Aggregate text properties using frequency analysis"""
    property_name: str
    metrics: TextMetrics
    top_occurrences_limit: Optional[int] = None

class BooleanPropertyAggregation(BaseModel):
    """Aggregate boolean properties using statistical functions"""
    property_name: str
    metrics: BooleanMetrics

class AggregationResult(BaseModel):
    """
    The aggregations to be performed on a collection in a vector database.

    They should be based on the original user query and can include multiple
    aggregations across different properties and metrics.
    """
    search_query: str | None = Field(
        description="The optional search query to be used for the aggregation."
    )
    groupby_property: str | None = Field(
        default=None,
        description="The property to group results by before applying aggregations",
    )
    aggregations: list[
        Union[
            IntegerPropertyAggregation,
            TextPropertyAggregation,
            BooleanPropertyAggregation,
        ]
    ] = Field(description="List of aggregations to perform on the collection")

# Evaluation Models
class Evaluation(BaseModel):
    """The answer and evaluation of the search and aggregation results."""
    search_answer: str | None = Field(
        description="The answer to the original query if it can be answered with the given information from the search results."
    )
    aggregation_answer: str | None = Field(
        description="The answer to the original query if it can be answered with the given information from the aggregation results."
    )
    has_aggregation_answer: bool = Field(
        description="Whether the aggregation answer is provided."
    )
    has_search_answer: bool = Field(
        description="Whether the search answer is provided."
    )
    is_partial_answer: bool = Field(description="Whether the answer is partial or not")
    missing_information: list[str] = Field(
        description="The missing information that is needed to answer the query"
    )

class EvaluateResult(BaseModel):
    """The result of the evaluation agent."""
    evaluation: Evaluation

# Router Agent
class SearchRouterAgentDeps:
    def __init__(self, collection_schemas: dict[str, dict[str, dict[str, str | bool]]]):
        self.collection_schemas = collection_schemas

    def build_prompt(self) -> str:
        return f"""
        You are a search query analyzer that determines which collections need which types of search actions.
        For each query, analyze which collections need:

        1. semantic search (searches): Used when you need to find or match specific items/documents
           - Break down complex queries into specific, focused search queries
           - Each search_query should target one specific aspect or question
           - For example, "what are laptop prices and battery life" should become two queries:
             * "what are laptop prices"
             * "what is laptop battery life"
        2. aggregations (aggregations): Used when you need to compute statistics, counts, averages, etc.
            - Each aggregation should be focused on one specific aspect of the original query

        Key Decision Rules:
        - A collection can appear in both searches and aggregations if needed
        - Use searches when you need to find specific information about items/documents
          - Find specific items
          - Match text or specific values
          - Filter by exact criteria
          - Break complex searches into multiple focused queries
        - Use aggregations when you need to compute statistics, counts, averages, etc.
          - Calculate statistics (avg, sum, count)
          - Group or summarize data
          - Analyze trends or patterns

        Example Response Format:
        {{
            "actions": {{
                "searches": [
                    {{
                        "query": "what are laptop prices",
                        "collection": {{"name": "products"}},
                    }}
                ],
                "aggregations": [
                    {{
                        "query": "average laptop price",
                        "collection": {{"name": "products"}}
                    }}
                ],
            }}
        }}

        The available collections and their schemas are:
        {self.collection_schemas}
        """

search_router_agent = Agent(
    deps_type=SearchRouterAgentDeps,
    result_type=SearchRouterResult,
    retries=RETRIES,
)

@search_router_agent.system_prompt
async def system_prompt(ctx: RunContext[SearchRouterAgentDeps]) -> str:
    """Generate the system prompt dynamically."""
    return ctx.deps.build_prompt()

@search_router_agent.result_validator
async def validate_collections(
    ctx: RunContext[SearchRouterAgentDeps], result: SearchRouterResult
) -> SearchRouterResult:
    """Validate that collections exist in the available schemas."""
    search_names = {sq.collection.name for sq in result.actions.searches}
    agg_names = {aq.collection.name for aq in result.actions.aggregations}
    all_collections = search_names | agg_names

    available = set(ctx.deps.collection_schemas.keys())

    if not all_collections.issubset(available):
        invalid = all_collections - available
        raise ModelRetry(f"Invalid collections specified: {invalid}")

    return result

# Query Agent
class QueryAgentDeps:
    def __init__(self, collection_schema: dict):
        self.collection_schema = collection_schema

    def get_available_filters(self) -> dict:
        """Get the available filter types based on property types in schema"""
        if not self.collection_schema:
            return {}

        available_filters = {}

        # Iterate directly through schema items instead of looking for 'properties' key
        for prop_name, prop_details in self.collection_schema.items():
            prop_type = prop_details.get("type")

            if prop_type in ["number", "integer"]:
                available_filters[prop_name] = {
                    "type": "number",
                    "operators": ["=", "<", ">", "<=", ">="],
                }
            elif prop_type in ["string", "text"]:
                available_filters[prop_name] = {
                    "type": "string",
                    "operators": ["=", "LIKE"],
                }
            elif prop_type == "boolean":
                available_filters[prop_name] = {
                    "type": "boolean",
                    "operators": ["=", "!="],
                }
        return available_filters

    def build_prompt(self) -> str:
        filters = self.get_available_filters()
        filter_instructions = ""
        if filters:
            filter_instructions = "\nAvailable filters for properties:\n"
            for prop, details in filters.items():
                filter_instructions += (
                    f"- {prop} ({details['type']}): {', '.join(details['operators'])}\n"
                )

        return f"""
        You are an expert query generator that decomposes a user query into one or more
        constituent queries and optional filters that will be applied for a vector database search.

        IMPORTANT: You must strictly respect property types when creating filters:
        - For number/integer properties: use IntegerPropertyFilter
        - For string/text properties: use TextPropertyFilter
        - For boolean properties: use BooleanPropertyFilter with only true/false values

        Each query should be paired with its own set of filters. For example, if the user asks
        "find Nike shoes under $100 and Puma shoes under $80", this should generate:
        - Query 1: "Nike shoes" with filters [price < 100]
        - Query 2: "Puma shoes" with filters [price < 80]

        Generate appropriate filters when the user query contains specific criteria
        that match the available filter properties. Only use text filters for exact matches,
        or LIKE operators with the following pattern matching syntax:
        - '?' matches exactly one unknown character
          Example: 'car?' matches 'cart', 'care', but not 'car'
        - '*' matches zero, one, or more unknown characters
          Example: 'car*' matches 'car', 'care', 'carpet'
          Example: '*car*' matches 'car', 'healthcare', 'scar'

        For text properties:
        - Use '=' for exact matches
        - Use 'LIKE' with wildcards for pattern matching

        Use LIKE mostly if the original query specifies a term or keyword must be matched, otherwise
        it is better to use the search query to discover semantic matches.

        IMPORTANT: Do not create a LIKE or = filter for a term that is too wordy or vague, it will not return any results.
        LIKE queries are usually best suited with specific single terms or keywords.


        Filter operations:
        - Use 'AND' when all filters must match (e.g., "shoes under $100 AND in red color")
        - Use 'OR' when any filter can match (e.g., "shoes in size 9 OR size 10")


        Some tips on how to decompose queries:
        - If the user query contains multiple conditions, decompose into multiple queries
        - If the user query contains a condition that is not supported by the available filters,
          decompose into multiple queries
        - If the user query contains a term that is a abbreviation or acronym you should try to expand the term to the full form
          while keeping the original query structure.

        Examples:
        1. Multiple conditions:
           User query: "find red shoes under $50 or blue shoes under $100"
           Result:
           - Query 1: "red shoes" with filters [price < 50]
           - Query 2: "blue shoes" with filters [price < 100]

        2. Unsupported filter conditions:
           User query: "find shoes that are waterproof and available in size 10"
           Result:
           - Query 1: "waterproof shoes"  # waterproof isn't a filter, so it's part of the query
           - Query 2: "shoes" with filters [size = 10]

        3. Abbreviations/acronyms:
           User query: "find AI courses with PhD instructors"
           Result:
           - Query: "artificial intelligence courses PhD instructors"  # expanded AI to artificial intelligence

        Filter instructions:

        {filter_instructions}
        """

query_agent = Agent(
    deps_type=QueryAgentDeps,
    result_type=QueryResult,
    retries=RETRIES,
)

@query_agent.system_prompt
async def system_prompt(ctx: RunContext[QueryAgentDeps]) -> str:
    return ctx.deps.build_prompt()

@query_agent.result_validator
async def validate_query(
    ctx: RunContext[QueryAgentDeps], result: QueryResult
) -> QueryResult:
    """Validate that the queries and filters are correct."""
    if not isinstance(result.queries, list):
        raise ModelRetry("The queries must be a list of strings.")
    if not result.queries:
        raise ModelRetry("The queries must not be empty.")

    if len(result.queries) != len(result.filters):
        raise ModelRetry(
            "Number of queries must match number of filter lists - each query "
            f"({len(result.queries)}) needs its own filter list ({len(result.filters)})"
        )

    return result

# Aggregation Agent
class AggregationAgentDeps:
    def __init__(self, collection_schema: dict):
        self.collection_schema = collection_schema

    def get_available_aggregations(self) -> dict:
        """Get the available aggregation types based on property types in schema"""
        if not self.collection_schema:
            return {}

        available_aggregations = {}

        # Iterate directly through schema items instead of looking for 'properties' key
        for prop_name, prop_details in self.collection_schema.items():
            prop_type = prop_details.get("type")

            if prop_type in ["number", "integer"]:
                available_aggregations[prop_name] = {
                    "type": "number",
                    "metrics": [m.value for m in NumericMetrics],
                }
            elif prop_type in ["string", "text"]:
                available_aggregations[prop_name] = {
                    "type": "string",
                    "metrics": [m.value for m in TextMetrics],
                }
            elif prop_type == "boolean":
                available_aggregations[prop_name] = {
                    "type": "boolean",
                    "metrics": [m.value for m in BooleanMetrics],
                }

        return available_aggregations

    def build_prompt(self) -> str:
        aggregations = self.get_available_aggregations()
        aggregation_instructions = ""
        if aggregations:
            aggregation_instructions = "\nAvailable aggregations for properties:\n"
            for prop, details in aggregations.items():
                aggregation_instructions += (
                    f"- {prop} ({details['type']}): {', '.join(details['metrics'])}\n"
                )

        return f"""
        You are an aggregation generator that determines appropriate statistical
        aggregations based on a user query.

        IMPORTANT RULES FOR AGGREGATIONS:
        1. Do NOT use search_query for filtering conditions. Instead, use the appropriate aggregation metrics.
        2. When grouping results:
           - Use groupby_property for comparing metrics across different categories
           - groupBy only works with a single property (no nested paths)
           - The property must exist in the collection schema

        Available metrics per property type:

        Numeric properties support:
        - COUNT: Total number of values
        - MIN: Minimum value
        - MAX: Maximum value
        - MEAN: Average value
        - MEDIAN: Middle value
        - MODE: Most frequent value
        - SUM: Sum of all values
        - TYPE: Data type information

        Text properties support:
        - COUNT: Total number of values
        - TOP_OCCURRENCES: Most frequent values (requires top_occurrences_limit)
        - TYPE: Data type information

        Boolean properties support:
        - COUNT: Total number of values
        - TOTAL_TRUE: Count of true values
        - TOTAL_FALSE: Count of false values
        - PERCENTAGE_TRUE: Percentage of true values
        - PERCENTAGE_FALSE: Percentage of false values
        - TYPE: Data type information

        {aggregation_instructions}

        When generating aggregations:
        1. For boolean filters (e.g., is_premium=true), use TOTAL_TRUE/TOTAL_FALSE metrics
        2. For numeric comparisons, use appropriate metrics (MIN, MAX, MEAN, etc.)
        3. When comparing across categories, use groupby_property
        4. For text analysis, use TOP_OCCURRENCES with a reasonable limit (e.g., 5-10)
        5. Include all relevant aggregations needed to fully answer the query

        Example queries and their aggregations:
        - "What's the average view count of premium articles?"
           -> Use BooleanPropertyAggregation with TOTAL_TRUE on is_premium
           -> Use IntegerPropertyAggregation with MEAN on view_count

        - "Show me view counts by category"
           -> Set groupby_property="category"
           -> Use IntegerPropertyAggregation with metrics like COUNT, MEAN, MIN, MAX on view_count

        - "What are the most common tags?"
           -> Use TextPropertyAggregation with TOP_OCCURRENCES on tags property
           -> Set top_occurrences_limit=5
        """

aggregation_agent = Agent(
    deps_type=AggregationAgentDeps,
    result_type=AggregationResult,
    retries=RETRIES,
)

@aggregation_agent.system_prompt
async def system_prompt(ctx: RunContext[AggregationAgentDeps]) -> str:
    return ctx.deps.build_prompt()

# TODO: add more validation to ensure that the aggregations are valid
@aggregation_agent.result_validator
async def validate_aggregation(
    ctx: RunContext[AggregationAgentDeps], result: AggregationResult
) -> AggregationResult:
    """Validate that the aggregations are not empty and properly formatted."""
    if not result.aggregations:
        raise ModelRetry("The aggregations must not be empty.")
    return result

# Evaluation Agent
class EvaluateAgentDeps:
    def __init__(
        self,
        original_query: str,
        search_results: list[str],
        aggregation_results: list[str],
    ) -> None:
        self.original_query = original_query
        self.search_results = search_results
        self.aggregation_results = aggregation_results

    def build_prompt(self) -> str:
        sections = []

        # Add original query
        sections.append(f'Original Query: "{self.original_query}"')

        sections.append("\nAvailable Information:")

        # Add search results section if exists
        if self.search_results:
            search_results_summary = "\n".join(
                f"- {result}..." for result in self.search_results
            )
            sections.append(f"\nSearch Results:\n{search_results_summary}")

        # Add aggregation results section if exists
        if self.aggregation_results:
            aggregation_results_summary = "\n".join(
                f"- {result}" for result in self.aggregation_results
            )
            sections.append(f"\nAggregation Results:\n{aggregation_results_summary}")

        # Add evaluation instructions
        sections.append(
            """
            You are an expert and precise evaluator of search and aggregation results. Your job to
            determine if the search and aggregation results are relevant to the original query.

            Your task is to evaluate:
            1. Whether the search results contain relevant information to answer the query
            2. Whether the aggregation results provide necessary statistical insights
            3. If the combination of both results fully answers the original query

        Consider the following in your evaluation and answer:
        - Are all parts of the original query addressed and satisfied?
        - Is there sufficient context in the search results?
        - Do the aggregations provide relevant statistical information?
        - Are there any missing pieces of information?
        - Is the information specific and precise enough?

        IMPORTANT:
        Pay close attention to the original query and the information provided and
        determine if the answers you are viewing correctly satisfy the original query.

        Your answers should only be based on the information provided, if there is no information
        in the search or aggregation results, you should not provide an answer.
        """
        )

        return "\n".join(sections)

evaluate_agent = Agent(
    deps_type=EvaluateAgentDeps,
    result_type=EvaluateResult,
    retries=RETRIES,
)

@evaluate_agent.system_prompt
async def system_prompt(ctx: RunContext[EvaluateAgentDeps]) -> str:
    return ctx.deps.build_prompt()

@evaluate_agent.result_validator
async def validate_evaluation(
    ctx: RunContext[EvaluateAgentDeps], result: EvaluateResult
) -> EvaluateResult:
    """Validate that the evaluation is not empty and that partial answers have missing information."""
    if not result.evaluation:
        raise ModelRetry("The evaluation must not be empty.")

    if (
        result.evaluation.is_partial_answer
        and not result.evaluation.missing_information
    ):
        raise ModelRetry("Partial answers must specify what information is missing.")

    return result