from typing import Optional, List, Dict, Callable, Any
from datetime import datetime
import json
import requests
import weaviate
from abc import ABC, abstractmethod
from pydantic import BaseModel
import os

from src.models import (
    WeaviateQueryWithSchema, 
    WeaviateQuery,
    QueryPredictionResult,
    ExperimentSummary,
    Tool,
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation
)
from src.lm.lm import LMService
from src.utils.weaviate_fc_utils import (
    get_collections_info,
    build_weaviate_query_tool_for_openai,
    build_weaviate_query_tool_for_anthropic,
    build_weaviate_query_tool_for_ollama,
    build_weaviate_query_tool_for_cohere,
    build_weaviate_query_tool_for_together
)
from src.utils.tool_with_rationale import build_weaviate_query_tool_for_openai_with_rationale
from src.utils.tool_per_collection import build_one_tool_per_collection
from src.utils.load_queries import load_queries
from src.utils.util import pretty_print_weaviate_query
from src.utils.metrics import abstract_syntax_tree_match_score

class ExperimentConfig(BaseModel):
    """Configuration for experiment execution."""
    model_provider: str
    model_name: str 
    api_key: str
    generate_with_models: bool = True
    queries_per_schema: int = 64
    weaviate_url: str = "http://localhost:8080/v1/schema"
    experiment_type: str = "standard"  # standard, rationale, per_collection, structured, parallel
    parallel_tool_calls: bool = False

class DatabaseManager:
    """Manages Weaviate database operations."""
    def __init__(self, weaviate_client, schema_url):
        self.client = weaviate_client
        self.schema_url = schema_url

    def reset_database(self):
        self.client.collections.delete_all()

    def create_schema_from_query(self, query: WeaviateQueryWithSchema):
        for class_schema in query.database_schema.weaviate_collections:
            schema_dict = {
                'class': class_schema.name,
                'description': class_schema.envisioned_use_case_overview,
                'properties': [
                    {
                        'name': prop.name,
                        'description': prop.description,
                        'dataType': prop.data_type
                    }
                    for prop in class_schema.properties
                ],
                'vectorizer': 'text2vec-transformers',
                'vectorIndexType': 'hnsw'
            }
            
            response = requests.post(
                url=self.schema_url,
                data=json.dumps(schema_dict),
                headers={'Content-Type': 'application/json'}
            )
            print(f"\033[92mCreated collection: {schema_dict['class']}\033[0m")

class BaseExperiment(ABC):
    """Base class for all experiment types."""
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.db_manager = DatabaseManager(
            weaviate.connect_to_local(),
            config.weaviate_url
        )
        self.lm_service = LMService(
            model_provider=config.model_provider,
            model_name=config.model_name,
            api_key=config.api_key
        )
        # Initialize metrics tracking
        self.total_ast_score = 0.0
        self.perfect_matches = 0
        self.total_queries = 0

    @abstractmethod
    def build_tools(self, collections_description: str, collections_enum: List[str]) -> List[Tool]:
        """Build appropriate tools based on experiment type."""
        pass

    @abstractmethod
    def process_tool_response(self, response: Any, nl_query: str) -> Optional[WeaviateQuery]:
        """Process the tool response into a WeaviateQuery."""
        pass

    def run(self):
        """Execute the experiment workflow."""
        print(f"\033[92m=== Starting {self.config.experiment_type.title()} Experiment ===\033[0m")
        
        queries = load_queries("../../data/synthetic-weaviate-queries-with-schemas.json")
        detailed_results = []
        per_schema_scores = {}
        successful_predictions = failed_predictions = 0
        
        self._initialize_first_schema(queries[0])
        
        for idx, query in enumerate(queries):
            if self._should_update_schema(idx):
                self._update_schema_and_scores(idx, queries[idx], detailed_results, per_schema_scores)
            
            result = self._process_single_query(idx, query)
            detailed_results.append(result)
            
            if result.error is None:
                successful_predictions += 1
                # Update metrics
                self.total_queries += 1
                self.total_ast_score += result.ast_score
                if result.ast_score == 1.0:
                    self.perfect_matches += 1
                # Print current metrics
                avg_ast = self.total_ast_score / self.total_queries
                perfect_pct = (self.perfect_matches / self.total_queries) * 100
                print(f"\033[93mCurrent Metrics (After {self.total_queries} queries):")
                print(f"Average AST Score: {avg_ast:.3f}")
                print(f"Perfect Matches: {self.perfect_matches}/{self.total_queries} ({perfect_pct:.1f}%)\033[0m")
            else:
                failed_predictions += 1

        summary = self._create_summary(queries, successful_predictions, failed_predictions,
                                    detailed_results, per_schema_scores)
        self._save_results(summary)
        self._print_summary(summary)
        
        self.db_manager.client.close()

    def _build_query_from_args(self, args: Dict, nl_query: str) -> WeaviateQuery:
        """Constructs a WeaviateQuery from tool call arguments."""
        return WeaviateQuery(
            target_collection=args["collection_name"],
            search_query=args.get("search_query"),
            integer_property_filter=self._create_model_instance(IntPropertyFilter, args.get("integer_property_filter")),
            text_property_filter=self._create_model_instance(TextPropertyFilter, args.get("text_property_filter")),
            boolean_property_filter=self._create_model_instance(BooleanPropertyFilter, args.get("boolean_property_filter")),
            integer_property_aggregation=self._create_model_instance(IntAggregation, args.get("integer_property_aggregation")),
            text_property_aggregation=self._create_model_instance(TextAggregation, args.get("text_property_aggregation")),
            boolean_property_aggregation=self._create_model_instance(BooleanAggregation, args.get("boolean_property_aggregation")),
            groupby_property=args.get("groupby_property"),
            corresponding_natural_language_query=nl_query
        )

    def _create_model_instance(self, model_class, data):
        """Creates a model instance if data is provided."""
        return model_class(**data) if data is not None else None

    def _initialize_first_schema(self, first_query):
        """Initialize the database with the first schema."""
        self.db_manager.reset_database()
        self.db_manager.create_schema_from_query(first_query)

    def _should_update_schema(self, idx: int) -> bool:
        """Determine if schema should be updated."""
        return idx > 0 and idx % self.config.queries_per_schema == 0

    def _update_schema_and_scores(self, idx: int, query: WeaviateQueryWithSchema,
                                detailed_results: List[QueryPredictionResult],
                                per_schema_scores: Dict[int, float]):
        """Update schema and calculate scores."""
        schema_idx = (idx // self.config.queries_per_schema) - 1
        per_schema_scores[schema_idx] = sum(
            r.ast_score for r in detailed_results[-self.config.queries_per_schema:]
        ) / self.config.queries_per_schema
        
        self._initialize_first_schema(query)

    def _process_single_query(self, idx: int, query: WeaviateQueryWithSchema) -> QueryPredictionResult:
        """Process a single query and return its result."""
        schema_idx = idx // self.config.queries_per_schema
        nl_query = query.corresponding_natural_language_query
        
        # Print natural language query in red
        print(f"\n\033[91mNatural Language Query: {nl_query}\033[0m")
        
        try:
            collections_description, collections_enum = get_collections_info(self.db_manager.client)
            tools = self.build_tools(collections_description, collections_enum)
            
            response = self.lm_service.one_step_function_selection_test(
                prompt=nl_query,
                tools=tools,
                parallel_tool_calls=self.config.parallel_tool_calls
            )
            
            predicted_query = self.process_tool_response(response, nl_query)
            
            if predicted_query is None:
                return self._create_error_result(idx, schema_idx, nl_query, query, "No tool called")
            
            # Print predicted query in cyan
            print(f"\033[96mPredicted Query:")
            print(pretty_print_weaviate_query(predicted_query))
            print("\033[0m")
            
            # Print ground truth query in white
            print(f"Ground Truth Query:")
            print(pretty_print_weaviate_query(query))
            
            ast_score = abstract_syntax_tree_match_score(predicted_query, query)
            return QueryPredictionResult(
                query_index=idx,
                database_schema_index=schema_idx,
                natural_language_query=nl_query,
                ground_truth_query=query,
                predicted_query=predicted_query,
                tool_rationale="",
                ast_score=ast_score,
                error=None
            )
            
        except Exception as e:
            return self._create_error_result(idx, schema_idx, nl_query, query, str(e))

    def _create_error_result(self, idx: int, schema_idx: int, nl_query: str,
                           query: WeaviateQueryWithSchema, error: str) -> QueryPredictionResult:
        """Create an error result."""
        return QueryPredictionResult(
            query_index=idx,
            database_schema_index=schema_idx,
            natural_language_query=nl_query,
            ground_truth_query=query,
            predicted_query=None,
            tool_rationale="",
            ast_score=0.0,
            error=error
        )

    def _create_summary(self, queries: List[WeaviateQueryWithSchema], successful_predictions: int,
                       failed_predictions: int, detailed_results: List[QueryPredictionResult],
                       per_schema_scores: Dict[int, float]) -> ExperimentSummary:
        """Create a summary of experiment results."""
        return ExperimentSummary(
            timestamp=datetime.now().isoformat(),
            model_provider=self.config.model_provider,
            model_name=self.config.model_name,
            experiment_type=self.config.experiment_type,
            total_queries=len(queries),
            successful_predictions=successful_predictions,
            failed_predictions=failed_predictions,
            average_ast_score=self.total_ast_score / self.total_queries if self.total_queries > 0 else 0.0,
            perfect_matches=self.perfect_matches,
            per_schema_scores=per_schema_scores,
            detailed_results=detailed_results
        )

    def _save_results(self, summary: ExperimentSummary):
        """Save experiment results to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"experiment_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(summary.model_dump(), f, indent=2)
        print(f"\nResults saved to {filename}")

    def _print_summary(self, summary: ExperimentSummary):
        """Print experiment summary."""
        print("\n=== Experiment Summary ===")
        print(f"Model: {summary.model_provider}/{summary.model_name}")
        print(f"Experiment Type: {summary.experiment_type}")
        print(f"Total Queries: {summary.total_queries}")
        print(f"Successful Predictions: {summary.successful_predictions}")
        print(f"Failed Predictions: {summary.failed_predictions}")
        print(f"Average AST Score: {summary.average_ast_score:.3f}")
        print(f"Perfect Matches: {summary.perfect_matches}")
        print("\nPer Schema Scores:")
        for schema_idx, score in summary.per_schema_scores.items():
            print(f"Schema {schema_idx}: {score:.3f}")

class StandardExperiment(BaseExperiment):
    """Standard experiment implementation."""
    def build_tools(self, collections_description: str, collections_enum: List[str]) -> List[Tool]:
        tool_builders = {
            "ollama": lambda: [build_weaviate_query_tool_for_ollama(
                collections_description, collections_enum).model_dump()],
            "openai": lambda: [build_weaviate_query_tool_for_openai(
                collections_description, collections_enum)],
            "anthropic": lambda: [build_weaviate_query_tool_for_anthropic(
                collections_description, collections_enum)],
            "cohere": lambda: [build_weaviate_query_tool_for_cohere(
                collections_description, collections_enum)],
            "together": lambda: [build_weaviate_query_tool_for_together(
                collections_description, collections_enum)]
        }
        builder = tool_builders.get(self.config.model_provider)
        return builder() if builder else []

    def process_tool_response(self, response: Any, nl_query: str) -> Optional[WeaviateQuery]:
        if not response:
            return None
            
        tool_call_args = self._parse_tool_args(response)
        return self._build_query_from_args(tool_call_args, nl_query)

    def _parse_tool_args(self, response):
        if self.config.model_provider == "openai":
            return json.loads(response[0].function.arguments)
        elif self.config.model_provider in ["cohere", "together"]:
            return response
        else:
            raise ValueError(f"Unsupported model provider: {self.config.model_provider}")

class RationaleExperiment(BaseExperiment):
    """Experiment with tool rationale."""
    def build_tools(self, collections_description: str, collections_enum: List[str]) -> List[Tool]:
        return [build_weaviate_query_tool_for_openai_with_rationale(
            collections_description, collections_enum, self.config.generate_with_models)]

    def process_tool_response(self, response: Any, nl_query: str) -> Optional[WeaviateQuery]:
        if not response:
            return None
        
        tool_call_args = json.loads(response[0].function.arguments)
        return self._build_query_from_args(tool_call_args, nl_query)

class PerCollectionExperiment(BaseExperiment):
    """Experiment with one tool per collection."""
    def build_tools(self, collections_description: str, collections_enum: List[str]) -> List[Tool]:
        return build_one_tool_per_collection(
            collections_description, collections_enum, self.config.generate_with_models)

    def process_tool_response(self, response: Any, nl_query: str) -> Optional[WeaviateQuery]:
        if not response:
            return None
        
        tool_call = response[0].function
        collection_name = tool_call.name.replace("query_", "")
        tool_call_args = json.loads(tool_call.arguments)
        tool_call_args["collection_name"] = collection_name
        
        return self._build_query_from_args(tool_call_args, nl_query)

class ParallelToolCallsExperiment(BaseExperiment):
    """Experiment with parallel tool calls."""
    def __init__(self, config: ExperimentConfig):
        super().__init__(config)
        self.total_tool_calls = 0

    def build_tools(self, collections_description: str, collections_enum: List[str]) -> List[Tool]:
        return [build_weaviate_query_tool_for_openai(
            collections_description, collections_enum, self.config.generate_with_models)]

    def process_tool_response(self, response: Any, nl_query: str) -> Optional[WeaviateQuery]:
        if not response:
            return None

        best_query = None
        best_ast_score = -1

        for tool_call in response:
            tool_call_args = json.loads(tool_call.function.arguments)
            current_query = self._build_query_from_args(tool_call_args, nl_query)
            
            # We'll need the ground truth query to calculate the score
            # This is a limitation of the current implementation
            ast_score = 0  # placeholder
            
            if ast_score > best_ast_score:
                best_ast_score = ast_score
                best_query = current_query

        return best_query

def create_experiment(config: ExperimentConfig) -> BaseExperiment:
    """Factory function to create the appropriate experiment type."""
    experiment_types = {
        "standard": StandardExperiment,
        "rationale": RationaleExperiment,
        "per_collection": PerCollectionExperiment,
        "parallel": ParallelToolCallsExperiment
    }
    
    experiment_class = experiment_types.get(config.experiment_type)
    if not experiment_class:
        raise ValueError(f"Unknown experiment type: {config.experiment_type}")
    
    return experiment_class(config)

if __name__ == "__main__":
    # Example usage of the unified framework
    config = ExperimentConfig(
        model_provider="openai",
        model_name="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        experiment_type="standard",
        generate_with_models=False
    )
    
    experiment = create_experiment(config)
    experiment.run()