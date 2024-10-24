import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel
from lm_service import LMService  # Assuming the provided code is saved as lm_service.py

# Define a sample output model using Pydantic
class OutputModel(BaseModel):
    text: str
    number: int

# Sample prompt and output model for testing
sample_prompt = "Tell me a joke about chickens."
sample_output_model = OutputModel(text="Why did the chicken cross the road?", number=42)

def test_generate_equivalence():
    # Mock response for ollama
    ollama_response = {
        "message": {
            "content": sample_output_model.json()
        }
    }

    # Mock response for openai
    openai_response = MagicMock()
    openai_response.choices = [MagicMock()]
    openai_response.choices[0].message.parsed = sample_output_model

    # Mock the external API calls
    with patch('ollama.chat', return_value=ollama_response) as mock_ollama_chat, \
         patch('openai.OpenAI') as mock_openai_class:
        
        # Configure the mock for OpenAI
        mock_openai_instance = mock_openai_class.return_value
        mock_openai_instance.model.beta.chat.completions.parse.return_value = openai_response

        # Initialize LMService instances for both providers
        service_ollama = LMService(
            model_provider="ollama",
            model_name="llama3.1:8b"
        )
        service_openai = LMService(
            model_provider="openai",
            model_name="gpt-3.5-turbo",
            api_key="test_api_key"
        )

        # Generate outputs using both services
        output_ollama = service_ollama.generate(sample_prompt, sample_output_model)
        output_openai = service_openai.generate(sample_prompt, sample_output_model)

        # Parse the outputs into the OutputModel
        parsed_output_ollama = OutputModel.parse_raw(output_ollama)
        parsed_output_openai = output_openai  # Already an instance of OutputModel

        # Assert that the outputs are structurally equivalent
        assert parsed_output_ollama == parsed_output_openai

        # Optionally, print the outputs for manual verification
        print("Ollama Output:", parsed_output_ollama)
        print("OpenAI Output:", parsed_output_openai)
