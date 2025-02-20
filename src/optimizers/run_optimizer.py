from typing import Optional, List, Dict, Any
import asyncio
import json
import os
from datetime import datetime
import random

from pydantic import BaseModel
from colorama import Fore, Style

from src.models import (
    WeaviateQuery,
    WeaviateQueryWithSchema,
    QueryPredictionResult,
    ExperimentSummary
)
from src.lm.pydantic_agents.function_calling_agent import WeaviateFunctionCallingAgent
from src.optimizers.opro_agent import OPROAgent
from src.utils.load_queries import load_queries
import weaviate

class FunctionCallingAgentExperiment:
    """Base experiment class for evaluating function calling agents."""
    
    def __init__(
        self,
        weaviate_client,
        num_queries: int = 64,
        generate_with_models: bool = True,
        instruction: Optional[str] = None
    ):
        print(f"{Fore.CYAN}Initializing FunctionCallingAgentExperiment...{Style.RESET_ALL}")
        self.weaviate_client = weaviate_client
        self.num_queries = num_queries
        self.generate_with_models = generate_with_models
        self.instruction = instruction or (
            "You are a database query assistant that helps users get information from a Weaviate database. "
            "Your role is to:\n\n"
            "1. Carefully analyze the user's question to understand their information needs\n"
            "2. Review the available database collections and their properties to identify relevant data\n"
            "3. Construct appropriate database queries using these available query capabilities:\n"
            "   - Basic text search using search_query\n" 
            "   - Filtering on integer, text, or boolean properties\n"
            "   - Aggregations on numeric fields (count, mean, median, etc.)\n"
            "   - Aggregations on text fields (top occurrences)\n"
            "   - Aggregations on boolean fields (total true/false, percentage true/false)\n"
            "   - Grouping results by specific properties\n"
            "4. Execute queries iteratively if needed to gather complete information\n"
            "5. Format responses to:\n"
            "   - Directly answer the user's question\n"
            "   - Include relevant statistics and data points\n"
            "   - Explain calculations or aggregations\n"
            "   - Highlight key insights and patterns\n"
            "   - Suggest alternatives if no results found\n\n"
            "Remember to:\n"
            "- Use the most appropriate query operations for the question\n"
            "- Consider multiple queries if needed for complex questions\n"
            "- Validate results match the user's intent\n"
            "- Provide clear, well-structured responses"
        )
        
        # Initialize metrics tracking
        self.total_exact_score = 0.0
        self.perfect_matches = 0
        self.total_queries = 0
        self.successful_predictions = 0
        self.failed_predictions = 0        
    async def run_experiment(self):
        """Execute the experiment workflow."""
        print(f"\n{Fore.GREEN}=== Starting Function Calling Agent Experiment ==={Style.RESET_ALL}")
        
        # Load test queries
        print(f"{Fore.CYAN}Loading test queries...{Style.RESET_ALL}")
        queries = load_queries("../../data/updated-queries-with-schemas.json")
        print(f"{Fore.GREEN}Loaded {len(queries)} test queries{Style.RESET_ALL}")
        
        # Take random subset of queries
        queries = random.sample(queries, self.num_queries)
        print(f"{Fore.GREEN}Processing {len(queries)} queries{Style.RESET_ALL}")
        
        # Reset metrics at start of each experiment run
        self.total_exact_score = 0.0
        self.perfect_matches = 0
        self.total_queries = 0
        self.successful_predictions = 0
        self.failed_predictions = 0
        
        detailed_results = []
        
        for idx, query in enumerate(queries):
            try:
                result = await self._process_single_query(idx, query)
                if not result:
                    print(f"{Fore.RED}Failed to process query {idx + 1}. Returning None.{Style.RESET_ALL}")
                    continue
            except Exception as e:
                print(f"{Fore.RED}Critical error processing query {idx + 1}: {str(e)}{Style.RESET_ALL}")
                continue

            detailed_results.append(result)
            
            if result.error is None:
                self.successful_predictions += 1
                self.total_queries += 1
                weighted_score = self._calculate_weighted_score(result.predicted_query, result.ground_truth_query)
                self.total_exact_score += weighted_score
                if weighted_score == 1:
                    self.perfect_matches += 1
                
                # Print current metrics
                avg_score = self.total_exact_score / self.total_queries
                perfect_pct = (self.perfect_matches / self.total_queries) * 100
                print(f"\n{Fore.CYAN}Current Metrics (After {self.total_queries} queries):")
                print(f"Most Recent Weighted Score: {weighted_score:.3f}")
                print(f"Average Weighted Score: {avg_score:.3f}")
                print(f"Perfect Matches: {self.perfect_matches}/{self.total_queries} ({perfect_pct:.1f}%){Style.RESET_ALL}")
            else:
                self.failed_predictions += 1
                print(f"{Fore.RED}Error processing query: {result.error}{Style.RESET_ALL}")

        summary = self._create_summary(queries, detailed_results)
        self._save_results(summary)
        self._print_summary(summary)
        
        return summary

    def _calculate_weighted_score(self, predicted_query: Optional[WeaviateQuery], ground_truth_query: WeaviateQuery) -> float:
        """Calculate weighted score comparing predicted and ground truth queries."""
        if predicted_query is None:
            return 0.0
            
        score = 0.0
        weights = {
            'search_query': 0.3,
            'filters': 0.4,
            'groupby': 0.3
        }
        
        # Compare search query structure
        if bool(predicted_query.search_query) == bool(ground_truth_query.search_query):
            score += weights['search_query']
        
        # Compare filter structures
        filter_types_match = (
            bool(predicted_query.integer_property_filter) == bool(ground_truth_query.integer_property_filter) and
            bool(predicted_query.text_property_filter) == bool(ground_truth_query.text_property_filter) and
            bool(predicted_query.boolean_property_filter) == bool(ground_truth_query.boolean_property_filter) and
            bool(predicted_query.integer_property_aggregation) == bool(ground_truth_query.integer_property_aggregation) and
            bool(predicted_query.text_property_aggregation) == bool(ground_truth_query.text_property_aggregation) and
            bool(predicted_query.boolean_property_aggregation) == bool(ground_truth_query.boolean_property_aggregation)
        )
        if filter_types_match:
            score += weights['filters']
            
        # Compare groupby structure
        if bool(predicted_query.groupby_property) == bool(ground_truth_query.groupby_property):
            score += weights['groupby']
            
        return score

    async def _process_single_query(self, idx: int, query: WeaviateQueryWithSchema) -> QueryPredictionResult:
        """Process a single query and return its result."""
        nl_query = query.corresponding_natural_language_query
        
        print(f"\n{Fore.CYAN}Processing Query {idx + 1}:")
        print(f"Natural Language Query: {nl_query}{Style.RESET_ALL}")
        
        try:            
            print(f"{Fore.CYAN}Creating WeaviateFunctionCallingAgent...{Style.RESET_ALL}")
            agent = await WeaviateFunctionCallingAgent.create(
                query=nl_query,
                collections=json.dumps(query.database_schema.model_dump()),
                tenant=None,
                weaviate_client=self.weaviate_client,
                instruction=self.instruction
            )
            print(f"{Fore.GREEN}Successfully created agent{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}Running agent...{Style.RESET_ALL}")
            response = await agent.run()
            print(f"{Fore.GREEN}Agent run complete{Style.RESET_ALL}")
            
            # Extract and validate the actual query used from response
            if response.get("query_history"):
                print(f"{Fore.CYAN}Processing agent response...{Style.RESET_ALL}")
                
                best_score = 0.0
                best_query = None
                
                for query_entry in response["query_history"]:
                    predicted_query_dict = query_entry["query"]
                    
                    try:
                        predicted_query = WeaviateQuery(**predicted_query_dict)
                    except Exception as e:
                        print(f"{Fore.RED}Query validation error: {str(e)}{Style.RESET_ALL}")
                        continue
                    
                    print(f"\n{Fore.GREEN}Evaluating Predicted Query:")
                    print(f"{predicted_query}{Style.RESET_ALL}")
                    
                    weighted_score = self._calculate_weighted_score(predicted_query, query)
                    print(f"{Fore.GREEN}Weighted Score: {weighted_score}{Style.RESET_ALL}")
                    
                    if weighted_score > best_score:
                        best_score = weighted_score
                        best_query = predicted_query
                
                if best_query is None:
                    return self._create_error_result(idx, nl_query, query, "No valid queries found")
                
                print(f"\n{Fore.CYAN}Ground Truth Query:")
                print(f"{query}{Style.RESET_ALL}")
                
                print(f"\n{Fore.GREEN}Best Query Selected:")
                print(f"{best_query}")
                print(f"Best Score: {best_score}{Style.RESET_ALL}")
                
                return QueryPredictionResult(
                    query_index=idx,
                    database_schema_index=0,
                    natural_language_query=nl_query,
                    ground_truth_query=query,
                    predicted_query=best_query,
                    tool_rationale="",
                    ast_score=best_score,
                    error=None
                )
            else:
                print(f"{Fore.RED}No queries executed by agent{Style.RESET_ALL}")
                return self._create_error_result(
                    idx, nl_query, query, 
                    "No queries executed by agent"
                )
                
        except Exception as e:
            print(f"{Fore.RED}Error during query processing: {str(e)}{Style.RESET_ALL}")
            return self._create_error_result(idx, nl_query, query, str(e))

    def _create_error_result(self, idx: int, nl_query: str,
                           query: WeaviateQueryWithSchema, error: str) -> QueryPredictionResult:
        """Create an error result."""
        return QueryPredictionResult(
            query_index=idx,
            database_schema_index=0,
            natural_language_query=nl_query,
            ground_truth_query=query,
            predicted_query=None,
            tool_rationale="",
            ast_score=0.0,
            error=error
        )

    def _create_summary(self, queries: List[WeaviateQueryWithSchema],
                       detailed_results: List[QueryPredictionResult]) -> ExperimentSummary:
        """Create a summary of experiment results."""
        return ExperimentSummary(
            timestamp=datetime.now().isoformat(),
            model_name="function-calling-agent",
            generate_with_models=self.generate_with_models,
            total_queries=len(queries),
            successful_predictions=self.successful_predictions,
            failed_predictions=self.failed_predictions,
            average_ast_score=self.total_exact_score / self.total_queries if self.total_queries > 0 else 0.0,
            perfect_matches=self.perfect_matches,
            per_schema_scores={},
            detailed_results=detailed_results
        )

    def _save_results(self, summary: ExperimentSummary):
        """Save experiment results to a file."""
        timestamp = datetime.now().strftime("%m-%d-%y")
        filename = f"function-calling-agent-{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(summary.model_dump(), f, indent=2)
        print(f"\n{Fore.GREEN}Results saved to {filename}{Style.RESET_ALL}")

    def _print_summary(self, summary: ExperimentSummary):
        """Print experiment summary."""
        print(f"\n{Fore.CYAN}=== Experiment Summary ==={Style.RESET_ALL}")
        print(f"Total Queries: {summary.total_queries}")
        print(f"Successful Predictions: {summary.successful_predictions}")
        print(f"Failed Predictions: {summary.failed_predictions}")
        print(f"Average Weighted Score: {summary.average_ast_score:.3f}")
        print(f"Perfect Matches: {summary.perfect_matches}")

class OptimizedFunctionCallingExperiment(FunctionCallingAgentExperiment):
    """Enhanced experiment class that adds OPRO instruction optimization."""
    
    def __init__(
        self,
        weaviate_client,
        num_queries: int = 64,
        generate_with_models: bool = True,
        optimization_rounds: int = 5,
        initial_instruction: Optional[str] = None
    ):
        # Initialize base experiment with initial instruction
        super().__init__(weaviate_client, num_queries, generate_with_models, initial_instruction)
        
        # Initialize OPRO-specific attributes
        self.optimization_rounds = optimization_rounds
        self.instruction_history: List[Dict[str, Any]] = []

    def get_default_instruction(self) -> str:
        """Get the default instruction for the agent."""
        return (
            'When providing a final response:\n'
            '1. Start with a clear, direct answer\n'
            '2. Include supporting statistics and data points\n'
            '3. Provide meaningful context and insights\n'
            '4. Break down complex numbers or aggregations\n'
            '5. Highlight notable patterns or trends\n'
            '6. Explain implications of the findings\n'
            '7. If no results, explain why and suggest alternatives'
        )

    async def optimize_instructions(self) -> List[Dict[str, Any]]:
        """Run the instruction optimization process."""
        if not self.instruction:
            self.instruction = self.get_default_instruction()
            print(f"{Fore.YELLOW}Using default instruction as starting point{Style.RESET_ALL}")
            
        for round_num in range(self.optimization_rounds):
            print(f"\n{Fore.MAGENTA}=== OPRO Optimization Round {round_num + 1}/{self.optimization_rounds} ==={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Current instruction being evaluated:{Style.RESET_ALL}")
            print(f"{self.instruction}\n")
            
            # Run experiment with current instruction
            print(f"{Fore.YELLOW}Running experiment batch with current instruction...{Style.RESET_ALL}")
            summary = await self.run_experiment()
            
            # Record results
            self.instruction_history.append({
                'round': round_num + 1,
                'instruction': self.instruction,
                'score': summary.average_ast_score,
                'perfect_matches': summary.perfect_matches,
                'total_queries': summary.total_queries
            })
            
            if round_num < self.optimization_rounds - 1:  # Don't optimize after last round
                print(f"\n{Fore.MAGENTA}=== OPRO Optimization Phase ==={Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Analyzing performance data and generating improved instruction...{Style.RESET_ALL}")
                
                # Create OPRO agent
                opro_agent = await OPROAgent.create(
                    user_task="Optimize instruction for Weaviate query generation",
                    available_context=json.dumps(summary.model_dump()),
                    candidate_history=self.instruction_history
                )
                
                # Get optimized instruction
                result = await opro_agent.run()
                self.instruction = result['optimized_instruction']
                
                print(f"\n{Fore.MAGENTA}=== OPRO Generated New Instruction ==={Style.RESET_ALL}")
                print(f"{self.instruction}\n")
                
                print(f"{Fore.YELLOW}Performance metrics for this round:")
                print(f"Average Score: {summary.average_ast_score:.3f}")
                print(f"Perfect Matches: {summary.perfect_matches}/{summary.total_queries}")
                print(f"Success Rate: {(summary.successful_predictions/summary.total_queries)*100:.1f}%{Style.RESET_ALL}")
        
        return self.instruction_history

async def main():
    print(f"{Fore.CYAN}Initializing Weaviate client...{Style.RESET_ALL}")
    weaviate_client = weaviate.connect_to_local(
        headers = {
            "X-OpenAI-Api-Key": ""
        }
    )
    print(f"{Fore.GREEN}Weaviate client initialized{Style.RESET_ALL}")
    
    print(f"\n{Fore.MAGENTA}=== Starting OPRO Optimization Process ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Creating experiment with following parameters:")
    print(f"Number of queries per round: 5")
    print(f"Number of optimization rounds: 3{Style.RESET_ALL}")
    
    experiment = OptimizedFunctionCallingExperiment(
        weaviate_client=weaviate_client,
        num_queries=5,
        optimization_rounds=5
    )
    
    history = await experiment.optimize_instructions()
    
    print(f"\n{Fore.MAGENTA}=== OPRO Optimization History ==={Style.RESET_ALL}")
    for result in history:
        print(f"{Fore.YELLOW}Round {result['round']}:")
        print(f"Performance Score: {result['score']:.3f}")
        print(f"Perfect Matches: {result['perfect_matches']}/{result['total_queries']}")
        print(f"Instruction Used:{Style.RESET_ALL}")
        print(f"{result['instruction']}\n")
    
    weaviate_client.close()
    print(f"{Fore.MAGENTA}OPRO optimization process completed successfully{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(main())
