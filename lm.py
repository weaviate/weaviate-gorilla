import ollama
import openai
from typing import Literal
from pydantic import BaseModel

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


    def generate(self, prompt: str, output_model: BaseModel) -> str:
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
