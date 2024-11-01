import ollama
import openai
from typing import Literal
from pydantic import BaseModel
from models import TestLMConnectionModel
from weaviate_function_calling_schema import Tool, Function, ParameterProperty, Parameters

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
            case _:
                raise ValueError(f"Unsupported model provider: {self.model_provider}")

    def generate(
        self, 
        prompt: str, 
        output_model: BaseModel
        ) -> str:
        match self.model_provider:
            case "ollama":
                # Ollama doesn't take a BaseModel as input
                # -- so instead we will append this to the prompt
                prompt += f"\nRespond with the following JSON: {output_model.model_dump_json()}"
                response = self.lm_client.chat(
                    model="llama3.1:8b",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    format="json"
                )
                return response["message"]["content"]
            case "openai":
                response = self.lm_client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Follow the response format instructions."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format=output_model
                )
                return response.choices[0].message.parsed
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
        response = self.generate(prompt, TestLMConnectionModel)
        print("\033[92mLM Connection test:\033[0m")
        print(response)

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
        
    def one_step_function_selection_test(self, prompt: str, tools: list[Tool]):
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
            response = self.lm_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools
            )
            return response
        else:
            raise ValueError(f"Function calling not yet supporetd for the LMService with {self.model_provider}")

'''
Note, vLLM function call snippet:

https://docs.vllm.ai/en/latest/getting_started/examples/offline_chat_with_tools.html
'''