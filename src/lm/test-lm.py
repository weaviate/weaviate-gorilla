# NOTE THIS HAS ONLY TESTED COHERE AND TOGETHER!!

# Insert your API keys here
OPENAI_API_KEY = ""
ANTHROPIC_API_KEY = ""
COHERE_API_KEY = ""
TOGETHER_API_KEY = ""

import json
from lm import LMService
from src.models import (
    OpenAITool,
    AnthropicTool,
    OllamaTool,
    CohereTool,
    CohereFunction,
    CohereFunctionParameters,
    TogetherAITool,
    TogetherAIFunction,
    TogetherAIParameters
)
from src.models import TestLMConnectionModel, ResponseOrToolCalls

# A mock dictionary for the dictionary_lookup tool
COUNTRY_CAPITALS = {
    "France": "Paris",
    "Germany": "Berlin",
    "Japan": "Tokyo",
    "Italy": "Rome"
}

def run_tool_mock(tool_name: str, arguments: dict):
    """
    Mock execution of the dictionary_lookup tool.
    Looks up 'query' in the COUNTRY_CAPITALS dict.
    """
    if tool_name == "dictionary_lookup":
        query = arguments.get("query", "")
        # Naive approach: check if any country matches
        for country, capital in COUNTRY_CAPITALS.items():
            if country.lower() in query.lower():
                return f"The capital of {country} is {capital}."
        return "No known capital found for the query."
    return "Tool not recognized."

def test_provider_tool_call(provider: str, model_name: str, api_key: str | None, tool_class):
    """
    Tests if a given provider can sensibly call the dictionary_lookup tool.
    """
    print(f"\n--- Testing {provider.capitalize()} Tool Calling ---")
    service = LMService(
        model_provider=provider,
        model_name=model_name,
        api_key=api_key
    )

    # Define the dictionary_lookup tool in the format expected by each provider
    if provider == "openai":
        tools = [OpenAITool(
            name="dictionary_lookup",
            description="Lookup the capital of a country. Input should be a JSON with a 'query' field.",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_type=dict
        )]
    elif provider == "anthropic":
        tools = [AnthropicTool(
            name="dictionary_lookup",
            description="Lookup the capital of a country. Input: {\"query\":\"country name\"}",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_type=dict
        )]
    elif provider == "ollama":
        tools = [OllamaTool(
            name="dictionary_lookup",
            description="Lookup the capital of a country. Input: {\"query\":\"country name\"}",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_type=dict
        )]
    elif provider == "cohere":
        tools = [CohereTool(
            type="function",
            function=CohereFunction(
                name="dictionary_lookup",
                description="Lookup the capital of a country. Input: {\"query\":\"country name\"}",
                parameters=CohereFunctionParameters(
                    type="object",
                    properties={"query": {"type": "string"}},
                    required=["query"]
                )
            )
        )]
    elif provider == "together":
        tools = [TogetherAITool(
            type="function",
            function=TogetherAIFunction(
                name="dictionary_lookup",
                description="Lookup the capital of a country. Input: {\"query\":\"country name\"}",
                parameters=TogetherAIParameters(
                    type="object",
                    properties={"query": {"type": "string"}},
                    required=["query"]
                )
            )
        )]
    else:
        raise ValueError("Provider not supported for tool calling test.")

    prompt = "I want to know the capital of France. Please use the dictionary_lookup tool to find the answer."

    # Try to have the LLM pick and call the tool
    tool_call_response = service.one_step_function_selection_test(prompt, tools)
    print(f"{provider.capitalize()} tool call response:", tool_call_response)

    # If the tool call is returned, run our mock tool and print results
    if tool_call_response:
        # Depending on the provider, the structure might differ
        # For openai, anthropic, cohere: seems to return a dict
        # For ollama: returns the arguments directly as a dict
        # For together: returns tool_calls similar to OpenAI format
        if isinstance(tool_call_response, dict):
            arguments = tool_call_response
        else:
            # Handle OpenAI/Together style tool_calls
            if hasattr(tool_call_response[0], 'function'):
                arguments = json.loads(tool_call_response[0].function.arguments)
            else:
                arguments = tool_call_response
        
        result = run_tool_mock("dictionary_lookup", arguments)
        print(f"Mock tool execution result: {result}")
    else:
        print(f"{provider.capitalize()} did not call the tool.")

if __name__ == "__main__":
    # You can comment out tests for providers you don't have access keys for.

    # Test OpenAI
    # test_provider_tool_call("openai", "gpt-4", OPENAI_API_KEY, OpenAITool)

    # Test Anthropic
    # test_provider_tool_call("anthropic", "claude-3-sonnet-20240229", ANTHROPIC_API_KEY, AnthropicTool)

    # Test Ollama (assuming local model and no api_key needed)
    # test_provider_tool_call("ollama", "llama3.1:8b", None, OllamaTool)

    # Test Cohere
    # test_provider_tool_call("cohere", "command-r-plus", COHERE_API_KEY, CohereTool)

    # Test Together
    test_provider_tool_call("together", "mistralai/Mixtral-8x7B-Instruct-v0.1", TOGETHER_API_KEY, TogetherAITool)