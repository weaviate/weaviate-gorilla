import cohere
from typing import Literal

VectorizerModelProvider = Literal["cohere"]

class VectorizerService():
    def __init__(
            self,
            model_provider: VectorizerModelProvider,
            model_name: str,
            api_key: str | None = None
    ):
        self.model_provider = model_provider
        self.model_name = model_name
    
    def vectorizer(self, text: str) -> list[float]:
        pass

'''
ollama.embeddings(
  model='all-minilm',
  prompt='Llamas are members of the camelid family',
)
'''

'''
response = openai_client.embeddings.create(
    input="Your text string goes here",
    model="text-embedding-3-small"
)

print(response.data[0].embedding)
'''