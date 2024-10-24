import openai
import ollama
from typing import Literal

VectorizerModelProvider = Literal["openai", "ollama"]

'''
model_registry = {
    "openai": [
        "text-embedding-3-small"
    ],
    "ollama": [
        "all-minilm"
    ]
}
'''

class VectorizerService():
    def __init__(
            self,
            model_provider: VectorizerModelProvider,
            model_name: str,
            api_key: str | None = None
    ):
        self.model_provider = model_provider
        self.model_name = model_name
        match self.model_provider:
            case "ollama":
                self.vectorize_client = ollama
            case "openai":
                self.vectorize_client = openai.OpenAI(
                    api_key=api_key
                )
            case _:
                raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def vectorizer(self, text: str) -> list[float]:
        match self.model_provider:
            case "ollama":
                return self.vectorize_client.embeddings(
                    model=self.model_name,
                    prompt=text
                )
            case "openai":
                return  self.vectorize_client.embeddings.create(
                    input=text,
                    model=self.model_name
                ).data[0].embedding

    def connection_test(self) -> None:
        text = "this is a test"
        print("\033[92mVectorizer connection test:\033[0m")
        print(self.vectorizer(text)[:5])