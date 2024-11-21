import ollama
import openai
import anthropic
from typing import Literal
from pydantic import BaseModel
from src.models import TestLMConnectionModel
from src.utils.weaviate_fc_utils import (
    OpenAITool,
    AnthropicTool,
    OllamaTool
)
import json
import time

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
                if self.model_name == "gemini-1.5-pro" | self.model_name == "gemini-1.5-flash":
                    self.lm_client = openai.OpenAI(
                        api_key=api_key,
                        base_url="https://generativelanguage.googleapis.com/v1beta/"
                    )
                else:
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
                max_retries = 5
                base_delay = 15
                
                for attempt in range(max_retries):
                    try:
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
                        
                    except Exception as e:
                        if attempt == max_retries - 1:  # Last attempt
                            raise e
                        
                        # Calculate exponential backoff delay
                        delay = base_delay * (2 ** attempt)  # 10, 20, 40, 80, 160 seconds
                        print(f"Anthropic API call failed, retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                
            case _:
                raise ValueError(f"Unsupported model provider: {self.model_provider}")

    def connection_test(self) -> None:
        prompt = "Say hello"
        output_model = TestLMConnectionModel if self.model_provider == "openai" else None
        print(f"\033[96mPrinting prompt: {prompt}\nwith output model: {output_model}\033[0m")
        response = self.generate(prompt, output_model)
        print("\033[92mLM Connection test result:\033[0m")
        print(response)
    
    def one_step_function_selection_test(
            self, 
            prompt: str, 
            tools: list[OpenAITool] | list[AnthropicTool] | list[OllamaTool]
        ) -> dict | None:
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
            )
            
            response = response.choices[0].message
            
            if response.tool_calls:
                tool_call_args = json.loads(response.tool_calls[0].function.arguments)
                return tool_call_args
            else:
                return None
        
        if self.model_provider == "ollama":
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            response = self.lm_client.chat(
                model=self.model_name,
                messages=messages,
                tools=tools
            )
            if not response["message"].get("tool_calls"):
                return None
            else:
                # maybe also worth looking into how parallel fc is interfaced with ollama for this
                tool = response["message"]["tool_calls"][0]
                return tool["function"]["arguments"]

        if self.model_provider == "anthropic":
            max_retries = 5
            base_delay = 15
            
            for attempt in range(max_retries):
                try:
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
                        
                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise e
                    
                    # Calculate exponential backoff delay
                    delay = base_delay * (2 ** attempt)  # 10, 20, 40, 80, 160 seconds
                    print(f"Anthropic API call failed, retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
        else:
            raise ValueError(f"Function calling not yet supported for the LMService with {self.model_provider}")

'''
Note, vLLM function call snippet:

https://docs.vllm.ai/en/latest/getting_started/examples/offline_chat_with_tools.html
'''