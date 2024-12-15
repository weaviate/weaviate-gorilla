# Insert your API keys here
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY"
COHERE_API_KEY = "YOUR_COHERE_API_KEY"
# If Ollama requires a key or config, set it up here. Otherwise, leave it as None or empty.

from lm import LMService
from src.utils.weaviate_fc_utils import (
    OpenAITool,
    AnthropicTool,
    OllamaTool,
    CohereTool
)
from src.models import TestLMConnectionModel, ResponseOrToolCalls

def test_openai():
    print("\n--- Testing OpenAI ---")
    service = LMService(
        model_provider="openai",
        model_name="gpt-4",
        api_key=OPENAI_API_KEY
    )
    response = service.generate("What is the capital of France?")
    print("OpenAI Response:", response)

def test_anthropic():
    print("\n--- Testing Anthropic ---")
    service = LMService(
        model_provider="anthropic",
        model_name="claude-2",
        api_key=ANTHROPIC_API_KEY
    )
    response = service.generate("What is the capital of Germany?")
    print("Anthropic Response:", response)

def test_cohere():
    print("\n--- Testing Cohere ---")
    service = LMService(
        model_provider="cohere",
        model_name="command-nightly",
        api_key=COHERE_API_KEY
    )
    response = service.generate("Name a famous painting by Leonardo da Vinci.")
    print("Cohere Response:", response)

def test_ollama():
    print("\n--- Testing Ollama ---")
    # Assuming Ollama is running locally and does not require an API key
    service = LMService(
        model_provider="ollama",
        model_name="llama3.1:8b"
    )
    response = service.generate("What is the capital of Japan?")
    print("Ollama Response:", response)

def test_function_selection_openai():
    print("\n--- Testing OpenAI Function Selection ---")
    service = LMService(
        model_provider="openai",
        model_name="gpt-4",
        api_key=OPENAI_API_KEY
    )
    tools = [OpenAITool(
        name="some_tool",
        description="A tool for demonstration",
        parameters={},
        output_type=dict
    )]
    tool_call_response = service.one_step_function_selection_test("Use the tool to find the meaning of life.", tools)
    print("Tool call response:", tool_call_response)

if __name__ == "__main__":
    # Run tests one by one
    # Remove or comment out tests that you don't have keys for or don't want to run.
    test_openai()
    test_anthropic()
    test_cohere()
    test_ollama()
    test_function_selection_openai()
