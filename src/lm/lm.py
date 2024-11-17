import ollama
import openai
import anthropic
from typing import Literal
from pydantic import BaseModel
from src.models import TestLMConnectionModel
from src.utils.weaviate_fc_utils import (
    Tool, 
    Function, 
    ParameterProperty, 
    Parameters, 
    AnthropicTool, 
    AnthropicToolInputSchema
)
import json

LMModelProvider = Literal["ollama", "openai"]

class LMService():
    def __init__(
            self,
            model_provider: LMModelProvider,
            model_name: str,
            api_key: str | None = None
    ):
        self.model_provider = model_provider
        self.model_name = model_name
        match self.model_provider:
            case "ollama":
                self.lm_client = ollama
            case "openai":
                self.lm_client = openai.OpenAI(
                    api_key=api_key
                )
            case "anthropic":
                self.lm_client = anthropic.Anthropic(
                    api_key=api_key
                )
            case _:
                raise ValueError(f"Unsupported model provider: {self.model_provider}") 
        
        print("Running connection test:")
        self.connection_test()
    def generate(
        self, 
        prompt: str,
        output_model: BaseModel | None = None
        ) -> str | dict:
        match self.model_provider:
            case "ollama":
                messages = [{"role": "user", "content": prompt}]
                # Note, this isn't implemented
                if output_model:
                    # Create an instance with default values
                    model_instance = output_model(generic_response="Hello! This is a test response.")
                    # Append output format instructions if model provided
                    messages[0]["content"] += f"\nRespond with the following JSON: {model_instance.model_dump_json()}"
                
                response = self.lm_client.chat(
                    model="llama3.1:8b",
                    messages=messages,
                    format="json" if output_model else None
                )
                return response["message"]["content"]
                
            case "openai":
                messages = [
                    {"role": "system", "content": "You are a helpful assistant. Follow the response format instructions."},
                    {"role": "user", "content": prompt}
                ]
                
                if output_model:
                    response = self.lm_client.beta.chat.completions.parse(
                        model=self.model_name,
                        messages=messages,
                        response_format=output_model
                    )
                    return response.choices[0].message.parsed
                else:
                    response = self.lm_client.chat.completions.create(
                        model=self.model_name,
                        messages=messages
                    )
                    return response.choices[0].message.content
                    
            case "anthropic":
                messages = [{"role": "user", "content": prompt}]
                if output_model:
                    # Create an instance with default values
                    model_instance = output_model(generic_response="Hello! This is a test response.")
                    # Append output format instructions if model provided
                    messages[0]["content"] += f"\nRespond with the following JSON format: {model_instance.model_dump_json()}"
                
                response = self.lm_client.messages.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=1024
                )
                return response.content[0].text
                
            case _:
                raise ValueError(f"Unsupported model provider: {self.model_provider}")

    def generate_with_functions(
        self,
        prompt: str,
        output_model: BaseModel,
        function_calling_schema: dict
    ):
        """Generates with a function calling schema"""
        pass

    def connection_test(self) -> None:
        prompt = "Say hello"
        output_model = TestLMConnectionModel if self.model_provider == "openai" else None
        print(f"\033[96mPrinting prompt: {prompt}\nwith output model: {output_model}\033[0m")
        response = self.generate(prompt, output_model)
        print("\033[92mLM Connection test result:\033[0m")
        print(response)

    # switch this on `openai` | `anthropic`
    def connection_test_with_tools(self) -> None:
        prompt = "What is 18549023948 multiplied by 84392348?"
        tools = [Tool(
            type="function",
            function=Function(
                name="multiply",
                description="Multiply two numbers together",
                parameters=Parameters(
                    type="object",
                    properties={
                        "num1": ParameterProperty(
                            type="number",
                            description="The first number to multiply",
                        ),
                        "num2": ParameterProperty(
                            type="number",
                            description="The second number to multiply",
                        ),
                    },
                    required=["num1", "num2"],
                ),
            ),
        ).model_dump_json()]
    
    # This should parse the response here
    def one_step_function_selection_test(self, prompt: str, tools: list[Tool] | list[AnthropicTool]) -> dict | None:
        if self.model_provider == "openai":
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use the supplied tools to assist the user."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            # set `parallel_tool_calls=False` to only call a single tool (defaults true)
            # NOTE!!! It could be the case that the model doesn't prioritize the accuracy of a tool call as much when it "knows" (not sure if that's how OpenAI set this up ofc) that it calls multiple functions potentially
            response = self.lm_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools
            ).choices[0].message
            
            if response.tool_calls:
                response.choices[0].message
                tool_call_args = json.loads(response.tool_calls[0].function.arguments)
                return tool_call_args
            else:
                return None
            
        if self.model_provider == "anthropic":
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            response = self.lm_client.messages.create(
                model=self.model_name,
                max_tokens=4096,
                tools=[tool.model_dump() for tool in tools],
                messages=messages
            )
            if response.stop_reason == "tool_use":
                tool_use = next(block for block in response.content if block.type == "tool_use")
                tool_name, tool_input = tool_use.name, tool_use.input
                # future work will need to parse the name as well
                return tool_input
            else:
                return None
        else:
            raise ValueError(f"Function calling not yet supporetd for the LMService with {self.model_provider}")

'''
Note, vLLM function call snippet:

https://docs.vllm.ai/en/latest/getting_started/examples/offline_chat_with_tools.html
'''