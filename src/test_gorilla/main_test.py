from typing import Optional, List, Dict, Callable, Any
from datetime import datetime
import json
import os
import weaviate
from abc import ABC, abstractmethod
from pydantic import BaseModel

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

class DatabaseConfig(BaseModel):
    """Configuration for database connection."""
    weaviate_url: str
    weaviate_api_key: str
    openai_api_key: str

class ExperimentConfig(BaseModel):
    """Configuration for experiment execution."""
    model_provider: str
    model_name: str 
    api_key: str
    generate_with_models: bool = True
    queries_per_schema: int = 64
    experiment_type: str = "standard"  # standard, rationale, per_collection, structured, parallel
    parallel_tool_calls: bool = False
    db_config: DatabaseConfig
    queries_file: str = "../../data/weaviate-gorilla.json"
    output_dir: str = "./results"

def create_weaviate_client(config: DatabaseConfig) -> weaviate.Client:
    """Create a Weaviate client based on configuration."""
    # Connect to Weaviate Cloud
    return weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
        headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
    )

# Function to extract collections info from queries
def get_collections_info_from_queries(queries):
    """Get information about collections and their properties from queries."""
    try:
        collections_info = {}
        
        for query in queries:
            for collection in query.database_schema.weaviate_collections:
                collection_name = collection.name
                if collection_name not in collections_info:
                    collections_info[collection_name] = {
                        "description": collection.description,
                        "properties": {}
                    }
                
                # Add properties
                for prop in collection.properties:
                    collections_info[collection_name]["properties"][prop.name] = {
                        "dataType": prop.data_type,
                        "description": prop.description
                    }
        
        # Format the collections description
        collections_enum = list(collections_info.keys())
        collections_description = "Available collections:\n"
        
        for collection_name, info in collections_info.items():
            collections_description += f"- {collection_name}: {info['description']}\n"
            collections_description += "  Properties:\n"
            
            for prop_name, prop_info in info["properties"].items():
                prop_type = prop_info["dataType"]
                prop_desc = prop_info["description"]
                collections_description += f"  - {prop_name} ({prop_type}): {prop_desc}\n"
            
            collections_description += "\n"
        
        return collections_description, collections_enum
    
    except Exception as e:
        print(f"Error getting collections info: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Error retrieving schema", []

class BaseExperiment(ABC):
    """Base class for all experiment types."""
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.weaviate_client = create_weaviate_client(config.db_config)
        self.lm_service = LMService(
            model_provider=config.model_provider,
            model_name=config.model_name,
            api_key=config.api_key
        )
        # Initialize metrics tracking
        self.total_ast_score = 0.0
        self.perfect_matches = 0
        self.total_queries = 0
        
        # Ensure output directory exists
        os.makedirs(config.output_dir, exist_ok=True)

    @abstractmethod
    def build_tools(self, collections_description: str, collections_enum: List[str]) -> List[Tool]:
        """Build appropriate tools based on experiment type."""
        pass

    def _process_tool_response(self, response: Any, nl_query: str) -> Optional[WeaviateQuery]:
        """Process the tool response into a WeaviateQuery."""
        if not response:
            return None
        
        if isinstance(response, dict):
            # Handle Anthropic response format
            return self._build_query_from_args(response, nl_query)
        
        # Handle Gemini/OpenAI response format
        if isinstance(response, list) and hasattr(response[0], 'function'):
            tool_call = response[0].function
            tool_call_args = json.loads(tool_call.arguments)
            return self._build_query_from_args(tool_call_args, nl_query)
            
        # Handle other model provider formats
        return None

    def run(self):
        """Execute the experiment workflow."""
        print(f"\033[92m=== Starting {self.config.experiment_type.title()} Experiment ===\033[0m")
        
        # Load queries with custom function that handles the specific JSON format
        print(f"=== Loading Weaviate Queries ===")
        queries = load_queries(self.config.queries_file)
        print(f"Loaded {len(queries)} raw queries")
        
        # Get collections info from queries
        collections_description, collections_enum = get_collections_info_from_queries(queries)
        
        detailed_results = []
        per_schema_scores = {}
        successful_predictions = failed_predictions = 0
        schema_queries = {}
        
        # Group queries by schema
        for idx, query in enumerate(queries):
            schema_idx = idx // self.config.queries_per_schema
            if schema_idx not in schema_queries:
                schema_queries[schema_idx] = []
            schema_queries[schema_idx].append((idx, query))
        
        # Process each schema group
        for schema_idx, query_group in schema_queries.items():
            print(f"\n\033[92m=== Processing Schema {schema_idx} ===\033[0m")
            schema_results = []
            
            for idx, query in query_group:
                result = self._process_single_query(idx, schema_idx, query, collections_description, collections_enum)
                detailed_results.append(result)
                schema_results.append(result)
                
                if result.error is None:
                    successful_predictions += 1
                    # Update metrics
                    self.total_queries += 1
                    self.total_ast_score += result.ast_score
                    if result.ast_score >= 0.95:
                        self.perfect_matches += 1
                    # Print current metrics
                    avg_ast = self.total_ast_score / self.total_queries
                    perfect_pct = (self.perfect_matches / self.total_queries) * 100
                    print(f"\033[93mCurrent Metrics (After {self.total_queries} queries):")
                    print(f"Average AST Score: {avg_ast:.3f}")
                    print(f"Perfect Matches: {self.perfect_matches}/{self.total_queries} ({perfect_pct:.1f}%)\033[0m")
                else:
                    failed_predictions += 1
            
            # Calculate per schema score
            valid_results = [r for r in schema_results if r.error is None]
            if valid_results:
                per_schema_scores[schema_idx] = sum(r.ast_score for r in valid_results) / len(valid_results)
            else:
                per_schema_scores[schema_idx] = 0.0

        summary = self._create_summary(queries, successful_predictions, failed_predictions,
                                    detailed_results, per_schema_scores)
        self._save_results(summary)
        self._print_summary(summary)
        
        try:
            self.weaviate_client.close()
        except:
            print("Note: Could not properly close client connection")
    def _build_query_from_args(self, args: Dict, nl_query: str) -> WeaviateQuery:
        """Constructs a WeaviateQuery from tool call arguments."""
        collection_name = args.get("collection_name", "")
        if collection_name:
            # Ensure first letter is capitalized for consistency
            collection_name = collection_name[0].upper() + collection_name[1:] if collection_name else ""
            
        return WeaviateQuery(
            corresponding_natural_language_query=nl_query,
            target_collection=collection_name,
            search_query=args.get("search_query"),
            limit=args.get("limit", 5),
            integer_property_filter=self._create_model_instance(IntPropertyFilter, args.get("integer_property_filter")),
            text_property_filter=self._create_model_instance(TextPropertyFilter, args.get("text_property_filter")),
            boolean_property_filter=self._create_model_instance(BooleanPropertyFilter, args.get("boolean_property_filter")),
            integer_property_aggregation=self._create_model_instance(IntAggregation, args.get("integer_property_aggregation")),
            text_property_aggregation=self._create_model_instance(TextAggregation, args.get("text_property_aggregation")),
            boolean_property_aggregation=self._create_model_instance(BooleanAggregation, args.get("boolean_property_aggregation")),
            groupby_property=args.get("groupby_property"),
            total_count=args.get("total_count")
        )

    def _create_model_instance(self, model_class, data):
        """Creates a model instance if data is provided."""
        return model_class(**data) if data is not None else None

    def _process_single_query(self, idx: int, schema_idx: int, query: WeaviateQueryWithSchema, 
                             collections_description: str, collections_enum: List[str]) -> QueryPredictionResult:
        """Process a single query and return its result."""
        nl_query = query.corresponding_natural_language_query
        
        # Print natural language query in cyan
        print(f"\n\033[96mNatural Language Query: {nl_query}\033[0m")
        
        try:
            tools = self.build_tools(collections_description, collections_enum)

            prompt = f"""
You are a precision-focused Weaviate query generator. Your ONLY task is to output a final Weaviate query that EXACTLY matches the provided schema and NL query. Every element (collection names, property names, filter types, operators, numeric formats, aggregation metrics, and group-by properties) must be an exact match. No substitutions, derivations, or extra text is allowed. Do not reveal any internal reasoning.

Instructions:
1. Analyze the Schema & NL Query:
   • Use ONLY schema values for collection and property names (e.g., "Restaurants", "averageRating").
   • Extract the descriptive search query exactly from the NL query.
THIS IS VERY IMPORTANT!! PLEASE PAY CLOSE ATTENTION TO THIS EXPLANATION OF THE AVAILABLE OPERATORS!!
   • For filters:
       - Text: use Text Filter with LIKE.
       - Numeric: use Integer Filter with operators (=, <, >, <=, >=) and numeric values (include .0 if required).
       - Boolean: use Boolean Filter with "=" and value True.
   • For aggregations, use:
       - Text: TOP_OCCURRENCES.
       - Int: MIN, MAX, MEAN, MEDIAN, MODE, or SUM.
Again, for IntAggregation you have MIN, MAX, MEAN, MEDIAN, MODE, or SUM!!! DO NOT EVER TRY TO USE SOMETHING LIKE TOTAL_TRUE with an IntAggregation!! THIS IS EXTREMELY IMPORTANT!
       - Boolean: TOTAL_TRUE, TOTAL_FALSE, PERCENTAGE_TRUE, or PERCENTAGE_FALSE.
PLEASE REMEMBER THIS!! THIS IS HOW YOU COUNT OBJECTS!!!! DO NOT TRY TO COUNT in Aggregations!! 
   • If counting objects is needed, set total_count to true (do NOT use COUNT in aggregations!!! This is very important!!).
   • Group By must exactly match a schema property.

2. Verification (Internal Only):
   • Confirm every element exactly matches the schema—no extra filters or modifications.

3. Output Format (Output ONLY):
Weaviate Query Details:
  Target Collection: <exact collection>
  Search Query: <exact search text>
  Total Count: <true/false>
  [Filters if any:]
    • Filter Type: <Text Filter / Integer Filter / Boolean Filter>
    • Property: <exact property name>
    • Operator: <exact operator>
    • Value: <exact value>
  [Aggregations if any:]
    • Aggregation Type: <Text / Boolean / Integer Aggregation>
    • Property: <exact property name>
    • Metrics: <exact metric>
  Group By: <if applicable, exact property name>
  Natural Language Query: {nl_query}

User Query:
{nl_query}

Available Schema (Collections and Properties):
{collections_description}

Now, generate the final Weaviate query following these guidelines.
IMPORTANT!! Please remember, COUNT and TYPE are not valid aggregations for an IntAggregation, TextAggregation, or BooleanAggregation!
IMPORTANT!! Please remember to format your response as a function call with the arguments you have chosen.
IMPORTANT!! IT IS VERY COMMON TO OUTPUT INCORRECT `IntAggregation` METRICS! PLEASE NOTE!! For IntAggregation,
Input should be 'MIN', 'MAX', 'MEAN', 'MEDIAN', 'MODE' or 'SUM', otherwise you will get an error such as: [type=literal_error, input_value='COUNT', input_type=str]
THIS IS EXTERMELY IMPORTANT! YOUR NUMBER 1 FOCUS SHOULD BE TO MAKE SURE THESE QUERIES ARE CORRECTLY FORMATTED!!!
REMEMBER, DO NOT EVERY TRY TO USE, say COUNT, with an IntAggregation!! YOU COUNT WITH THE `total_count` ARGUMENT!!! IntAggregation only supporst MIN, MAX, MEAN, MEDIAN, MODE, or SUM!!
"""

            response = self.lm_service.one_step_function_selection_test(
                prompt=prompt,
                tools=tools,
                parallel_tool_calls=self.config.parallel_tool_calls
            )

            predicted_query = self._process_tool_response(response, nl_query)

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
            print(f"\033[91mError: {str(e)}\033[0m")
            import traceback
            traceback.print_exc()
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
            model_name=self.config.model_name,
            generate_with_models=self.config.generate_with_models,
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
        timestamp = datetime.now().strftime("%m-%d-%y")
        filename = os.path.join(
            self.config.output_dir, 
            f"{summary.model_name.replace('/', '-')}-{timestamp}.json"
        )
        with open(filename, 'w') as f:
            json.dump(summary.model_dump(), f, indent=2)
        print(f"\nResults saved to {filename}")

    def _print_summary(self, summary: ExperimentSummary):
        """Print experiment summary."""
        print("\n=== Experiment Summary ===")
        print(f"Model: {summary.model_name}")
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

class RationaleExperiment(BaseExperiment):
    """Experiment with tool rationale."""
    def build_tools(self, collections_description: str, collections_enum: List[str]) -> List[Tool]:
        return [build_weaviate_query_tool_for_openai_with_rationale(
            collections_description, collections_enum, self.config.generate_with_models)]

class PerCollectionExperiment(BaseExperiment):
    """Experiment with one tool per collection."""
    def build_tools(self, collections_description: str, collections_enum: List[str]) -> List[Tool]:
        return build_one_tool_per_collection(
            collections_description, collections_enum, self.config.generate_with_models)

    def _process_tool_response(self, response: Any, nl_query: str) -> Optional[WeaviateQuery]:
        if not response or not isinstance(response, list) or not hasattr(response[0], 'function'):
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
        config.parallel_tool_calls = True
        self.total_tool_calls = 0

    def build_tools(self, collections_description: str, collections_enum: List[str]) -> List[Tool]:
        return [build_weaviate_query_tool_for_openai(
            collections_description, collections_enum, self.config.generate_with_models)]

    def _process_tool_response(self, response: Any, nl_query: str) -> Optional[WeaviateQuery]:
        if not response or not isinstance(response, list):
            return None

        # In a real implementation, we might compare against ground truth
        # But for simplicity, we'll just take the first response
        if hasattr(response[0], 'function'):
            tool_call_args = json.loads(response[0].function.arguments)
            return self._build_query_from_args(tool_call_args, nl_query)
        
        return None

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
    # Direct configuration - no command line args
    # Replace these values with your actual credentials
    WEAVIATE_URL = ""
    WEAVIATE_API_KEY = ""
    OPENAI_API_KEY = "" # used for embeddings in Weaviate
    LM_API_KEY = ""

    db_config = DatabaseConfig(
        weaviate_url=WEAVIATE_URL,
        weaviate_api_key=WEAVIATE_API_KEY,
        openai_api_key=OPENAI_API_KEY
    )
    
    config = ExperimentConfig(
        model_provider="openai",
        model_name="gpt-4o-mini",
        api_key=LM_API_KEY,
        experiment_type="standard",
        generate_with_models=False,
        db_config=db_config,
        queries_file="../../data/weaviate-gorilla.json",  # Updated path
        output_dir="./results"
    )
    
    print("\n=== Experiment Configuration ===")
    print(f"Model Provider: {config.model_provider}")
    print(f"Model Name: {config.model_name}")
    print(f"Experiment Type: {config.experiment_type}")
    print(f"Database URL: {config.db_config.weaviate_url}")
    print(f"Queries File: {config.queries_file}")
    print(f"Output Directory: {config.output_dir}")
    print("===============================\n")
    
    # Create and run experiment
    try:
        experiment = create_experiment(config)
        experiment.run()
    except Exception as e:
        print(f"\033[91mError running experiment: {str(e)}\033[0m")
        import traceback
        traceback.print_exc()