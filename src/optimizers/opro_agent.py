from __future__ import annotations

import asyncio
import json
import time
from typing import List, Optional, Union
from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.result import Usage
from colorama import Fore, Style

@dataclass
class OPRODependencies:
    user_task: str
    available_context: str
    candidate_history: List[dict]
    instructions: str

class OPROResult(BaseModel):
    optimized_instruction: str = Field(description='The optimized instruction to try next')
    rationale: str = Field(description='Explanation for why this instruction should work better')

opro_agent = Agent(
    'openai:gpt-4o',
    deps_type=OPRODependencies,
    result_type=OPROResult
)

@opro_agent.system_prompt
async def build_prompt(ctx: RunContext[OPRODependencies]) -> str:
    # Format the candidate history into a human-readable string
    if ctx.deps.candidate_history:
        history_entries = []
        for i, entry in enumerate(ctx.deps.candidate_history):
            history_entries.append(
                f"Candidate {i+1}: {entry.get('instruction', 'N/A')} - Score: {entry.get('score', 'N/A')}"
            )
        history_str = "\n".join(history_entries)
    else:
        history_str = "No previous candidate instructions."

    return f"""
User Task: "{ctx.deps.user_task}"

Available Context:
{ctx.deps.available_context}

Previous Candidate Instructions and Scores:
{history_str}

Instructions:
{ctx.deps.instructions}
"""

class OPROAgent:
    def __init__(
        self,
        user_task: str,
        available_context: str,
        candidate_history: List[dict],
        instructions: str = (
            '- Generate a new candidate instruction that is distinct from previous candidates\n'
            '- Provide a clear rationale explaining why this candidate should perform better\n'
            '- Focus on improving weak points identified in previous candidates\n'
            '- Consider the specific context and requirements of the task\n'
            '- Aim for instructions that are clear, specific and actionable'
        ),
    ):
        print(f"{Fore.CYAN}Initializing OPROAgent...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Task: {user_task}{Style.RESET_ALL}")
        
        self.user_task = user_task
        self.available_context = available_context
        self.candidate_history = candidate_history
        self.instructions = instructions
        self.usage = Usage(request_tokens=0, requests=0, response_tokens=0, total_tokens=0)
        
        print(f"{Fore.CYAN}Initialization complete{Style.RESET_ALL}")

    @classmethod
    async def create(
        cls,
        user_task: str,
        available_context: str,
        candidate_history: List[dict],
        instructions: Optional[str] = None,
    ) -> "OPROAgent":
        return cls(user_task, available_context, candidate_history, instructions)

    async def run(self) -> dict:
        print(f"\n{Fore.CYAN}Starting OPRO agent run...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Task: {self.user_task}{Style.RESET_ALL}")
        
        t0 = time.time()
        
        print(f"{Fore.CYAN}Preparing dependencies for agent run...{Style.RESET_ALL}")
        deps = OPRODependencies(
            user_task=self.user_task,
            available_context=self.available_context,
            candidate_history=self.candidate_history,
            instructions=self.instructions
        )
        print(f"{Fore.CYAN}Dependencies prepared, executing agent...{Style.RESET_ALL}")

        result = await opro_agent.run(self.user_task, deps=deps)
        print(f"{Fore.YELLOW}Agent execution completed{Style.RESET_ALL}")

        total_time = time.time() - t0
        print(f"\n{Fore.CYAN}Agent run completed{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Total execution time: {total_time:.2f} seconds{Style.RESET_ALL}")
        
        return {
            "task": self.user_task,
            "optimized_instruction": result.data.optimized_instruction,
            "rationale": result.data.rationale,
            "usage": self.usage,
            "total_time": total_time,
        }

async def main():
    # Test data
    candidate_history = [
        {"instruction": "Provide a step-by-step explanation before answering.", "score": 3.5},
        {"instruction": "Include numerical statistics in your response.", "score": 3.0},
        {"instruction": "Answer concisely with key points.", "score": 2.8},
    ]
    
    available_context = json.dumps({
        "weaviate_collections": [{
            "name": "Restaurants",
            "properties": [
                {"name": "averageRating", "data_type": ["number"], "description": "Average rating out of 5"}
            ]
        }]
    })

    agent = await OPROAgent.create(
        user_task="What is the average rating of these Restaurants?",
        available_context=available_context,
        candidate_history=candidate_history
    )
    
    response = await agent.run()
    print(f"{Fore.YELLOW}Optimized Instruction: {response['optimized_instruction']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Rationale: {response['rationale']}{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(main())
