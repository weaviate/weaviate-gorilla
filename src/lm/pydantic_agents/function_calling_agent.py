from __future__ import annotations

import asyncio
import time
import json
from typing import List, Optional, Union
from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.result import Usage
from colorama import Fore, Style

import weaviate

from src.models import WeaviateQuery
from src.lm.pydantic_agents.function_calling_executor import query_collection

@dataclass
class WeaviateDependencies:
    query: str
    collections: str
    tenant: Optional[str]
    weaviate_client: any
    query_history: List[dict]
    available_collections: str
    instruction: str

class WeaviateResult(BaseModel):
    ready_to_respond: bool = Field(description='Whether we have enough info to respond')
    final_response: Optional[str] = Field(None, description='Final response to user if ready')
    database_query: Optional[WeaviateQuery] = Field(None, description='Next query to run if not ready')

weaviate_agent = Agent(
    'openai:gpt-4o',
    deps_type=WeaviateDependencies,
    result_type=WeaviateResult
)

@weaviate_agent.system_prompt
async def build_prompt(ctx: RunContext[WeaviateDependencies]) -> str:
    # Format query history with more context and structure
    if ctx.deps.query_history:
        history_entries = []
        for i, entry in enumerate(ctx.deps.query_history):
            query_details = entry['query']
            results = entry['results']
            
            # Format the query details
            query_str = f"Query {i+1} Details:\n"
            query_str += f"- Collection: {query_details.get('target_collection')}\n"
            if query_details.get('integer_property_aggregation'):
                query_str += f"- Aggregation: {query_details['integer_property_aggregation']['property_name']} "
                query_str += f"({query_details['integer_property_aggregation']['metrics']})\n"
            
            # Format the results with clear structure
            results_str = f"Results {i+1}:\n"
            if "Aggregation results" in results:
                for line in results.split('\n'):
                    if line.strip():
                        results_str += f"  {line.strip()}\n"
            else:
                results_str += f"  {results}\n"
            
            history_entries.append(f"{query_str}{results_str}")
        
        history_str = "\n".join(history_entries)
    else:
        history_str = "No previous queries."

    # Parse collections data to show available properties more clearly
    collections_data = json.loads(ctx.deps.available_collections)
    properties_str = ""
    for collection in collections_data["weaviate_collections"]:
        properties_str += f"\n\nCollection '{collection['name']}' has these properties:"
        for prop in collection["properties"]:
            properties_str += f"\n- {prop['name']} ({', '.join(prop['data_type'])}): {prop['description']}"

    return f"""
Instructions:
{ctx.deps.instruction}

User Query: "{ctx.deps.query}"

Available Collections and their Properties:{properties_str}

Previous Query History and Results:
--------------------------------
{history_str}
"""

@weaviate_agent.tool
async def query_weaviate(
    ctx: RunContext[WeaviateDependencies], 
    weaviate_query: WeaviateQuery
) -> str:
    """Execute a query against the Weaviate database"""
    result = query_collection(ctx.deps.weaviate_client, weaviate_query)
    # Add the query and result to the context's query history
    ctx.deps.query_history.append({
        "query": weaviate_query.model_dump(),
        "results": result
    })
    return result

class WeaviateFunctionCallingAgent:
    def __init__(
        self,
        query: str,
        collections: str,
        tenant: Optional[str],
        weaviate_client: any,
        instruction: str = (
            'When providing a final response:\n'
            '1. Start with a clear, direct answer\n'
            '2. Include supporting statistics and data points\n'
            '3. Provide meaningful context and insights\n'
            '4. Break down complex numbers or aggregations\n'
            '5. Highlight notable patterns or trends\n'
            '6. Explain implications of the findings\n'
            '7. If no results, explain why and suggest alternatives'
        ),
    ):
        print(f"{Fore.CYAN}Initializing WeaviateFunctionCallingAgent...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Query: {query}{Style.RESET_ALL}")
        
        self.query = query
        self.collections_data = json.loads(collections)
        self.tenant = tenant
        self.weaviate_client = weaviate_client
        self.usage = Usage(request_tokens=0, requests=0, response_tokens=0, total_tokens=0)
        self.available_collections = collections
        self.query_history = []
        self.instruction = instruction
        
        collection_names = [c["name"] for c in self.collections_data["weaviate_collections"]]
        print(f"{Fore.GREEN}Collections: {collection_names}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Initialization complete{Style.RESET_ALL}")

    @classmethod
    async def create(
        cls,
        query: str,
        collections: Union[str, str],
        tenant: Optional[str],
        weaviate_client: any,
        instruction: Optional[str] = None,
    ) -> "WeaviateFunctionCallingAgent":
        return cls(query, collections, tenant, weaviate_client, instruction)

    async def run(self) -> dict:
        print(f"\n{Fore.CYAN}Starting function-calling agent run...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Original query: {self.query}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Available collections: {[c['name'] for c in self.collections_data['weaviate_collections']]}{Style.RESET_ALL}")
        
        t0 = time.time()
        ready_to_respond = False
        final_response: Optional[str] = None
        max_iterations = 5

        iterations = 0
        while not ready_to_respond and iterations < max_iterations:
            iterations += 1
            print(f"\n{Fore.GREEN}Starting function calling iteration {iterations}/{max_iterations}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Current query history length: {len(self.query_history)}{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}Preparing dependencies for agent run...{Style.RESET_ALL}")
            deps = WeaviateDependencies(
                query=self.query,
                collections=self.available_collections,
                tenant=self.tenant,
                weaviate_client=self.weaviate_client,
                query_history=self.query_history,
                available_collections=self.available_collections,
                instruction=self.instruction
            )
            print(f"{Fore.CYAN}Dependencies prepared, executing agent...{Style.RESET_ALL}")

            result = await weaviate_agent.run(self.query, deps=deps)
            print(f"{Fore.YELLOW}Agent execution completed{Style.RESET_ALL}")
            
            if result.data.ready_to_respond:
                final_response = result.data.final_response
                ready_to_respond = True
                print(f"{Fore.YELLOW}Agent signaled readiness with final response{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Final response: {final_response}{Style.RESET_ALL}")
            else:
                weaviate_query = result.data.database_query
                print(f"{Fore.GREEN}Agent requested additional database query:{Style.RESET_ALL}")
                print(f"{Fore.GREEN}Query details: {weaviate_query}{Style.RESET_ALL}")
                
                print(f"{Fore.CYAN}Executing Weaviate query...{Style.RESET_ALL}")
                query_result = query_collection(self.weaviate_client, weaviate_query)
                print(f"{Fore.GREEN}Query execution completed{Style.RESET_ALL}")
                print(f"{Fore.GREEN}Query results: {query_result}{Style.RESET_ALL}")
                
                self.query_history.append({
                    "query": weaviate_query.model_dump(),
                    "results": query_result,
                })
                print(f"{Fore.YELLOW}Query history updated - new length: {len(self.query_history)}{Style.RESET_ALL}")

        if not ready_to_respond:
            print(f"{Fore.RED}Maximum iterations ({max_iterations}) reached without getting a final response{Style.RESET_ALL}")
            final_response = (
                "I apologize, but I was unable to provide a complete answer after several attempts. "
                "This might be because:\n"
                "1. The query is too complex and needs to be broken down\n"
                "2. The required data is not available in the current collections\n"
                "3. There might be an issue with the data format or accessibility\n\n"
                "Please try:\n"
                "- Rephrasing your question to be more specific\n"
                "- Breaking it into smaller, focused questions\n"
                "- Checking if the information you're looking for is available in the collections"
            )

        total_time = time.time() - t0
        print(f"\n{Fore.CYAN}Agent run completed{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Total execution time: {total_time:.2f} seconds{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Total queries executed: {len(self.query_history)}{Style.RESET_ALL}")
        
        return {
            "original_query": self.query,
            "final_response": final_response,
            "usage": self.usage,
            "total_time": total_time,
            "query_history": self.query_history,
        }

async def main():
    weaviate_client = weaviate.connect_to_local(
        headers={
            "X-OpenAI-Api-Key": ""
        }
    )

    agent = await WeaviateFunctionCallingAgent.create(
        query="Find restaurants offering Italian cuisine with a cozy atmosphere, with at least an average rating of 4.5. Also, calculate the percentage of these restaurants that are open and group results based on their open status.",
        collections="{\"weaviate_collections\":[{\"name\":\"Restaurants\",\"properties\":[{\"name\":\"name\",\"data_type\":[\"string\"],\"description\":\"The name of the restaurant.\"},{\"name\":\"description\",\"data_type\":[\"string\"],\"description\":\"A detailed description and summary of the restaurant, including cuisine type and ambiance.\"},{\"name\":\"averageRating\",\"data_type\":[\"number\"],\"description\":\"The average rating score out of 5 for the restaurant.\"},{\"name\":\"openNow\",\"data_type\":[\"boolean\"],\"description\":\"A flag indicating whether the restaurant is currently open.\"}],\"envisioned_use_case_overview\":\"This schema focuses on enabling users to discover restaurants based on a comprehensive profile. With semantic search, users can find restaurants by cuisine, ambiance, or special features.\"},{\"name\":\"Menus\",\"properties\":[{\"name\":\"menuItem\",\"data_type\":[\"string\"],\"description\":\"The name of the menu item.\"},{\"name\":\"itemDescription\",\"data_type\":[\"string\"],\"description\":\"A detailed description of the menu item, including ingredients and preparation style.\"},{\"name\":\"price\",\"data_type\":[\"number\"],\"description\":\"The price of the menu item.\"},{\"name\":\"isVegetarian\",\"data_type\":[\"boolean\"],\"description\":\"A flag to indicate if the menu item is vegetarian.\"}],\"envisioned_use_case_overview\":\"This schema assists in linking dining experiences with specific restaurants through their menus. Rich search features allow customers to find dishes tailored to dietary needs and price points.\"},{\"name\":\"Reservations\",\"properties\":[{\"name\":\"reservationName\",\"data_type\":[\"string\"],\"description\":\"The name under which the reservation is made.\"},{\"name\":\"notes\",\"data_type\":[\"string\"],\"description\":\"Detailed notes about the reservation, such as special requests or celebrations.\"},{\"name\":\"partySize\",\"data_type\":[\"number\"],\"description\":\"The number of persons in the reservation.\"},{\"name\":\"confirmed\",\"data_type\":[\"boolean\"],\"description\":\"A flag indicating whether the reservation is confirmed.\"}],\"envisioned_use_case_overview\":\"This schema integrates with the restaurants by managing booking experiences. Semantic search of reservations can uncover trends in dining preferences and commonly requested meal attributes.\"}]}",
        tenant=None,
        weaviate_client=weaviate_client
    )
    response = await agent.run()
    print(f"{Fore.YELLOW}Final Response: {response['final_response']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Query History: {response['query_history']}{Style.RESET_ALL}")

    weaviate_client.close()

if __name__ == "__main__":
    asyncio.run(main())
