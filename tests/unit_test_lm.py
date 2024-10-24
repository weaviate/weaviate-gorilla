# `pytest unit_test_lm.py`

import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel
from lm import LMService, LMModelProvider

class MockOutputModel(BaseModel):
    def model_dump_json(self):
        return '{"key": "value"}'

# Patch the correct target for ollama and openai
@patch('lm.openai.OpenAI')
@patch('lm.ollama')
def test_init_ollama(mock_ollama, mock_openai):
    # Initialize LMService with ollama provider
    service = LMService(model_provider="ollama", model_name="test_model")
    # Assert that the model provider is correctly set to ollama
    assert service.model_provider == "ollama"
    # Assert that the lm_client is correctly set to the mocked ollama
    assert service.lm_client == mock_ollama

# Patch the correct target for ollama and openai
@patch('lm.openai.OpenAI')
@patch('lm.ollama')
def test_init_openai(mock_ollama, mock_openai):
    # Mock the instance of openai
    mock_openai_instance = mock_openai.return_value
    # Initialize LMService with openai provider
    service = LMService(model_provider="openai", model_name="test_model", api_key="test_key")
    # Assert that the model provider is correctly set to openai
    assert service.model_provider == "openai"
    # Assert that the lm_client is correctly set to the mocked openai instance
    assert service.lm_client == mock_openai_instance

# Patch the correct target for ollama chat method
@patch('lm.ollama.chat')
def test_generate_ollama(mock_chat):
    # Mock the response of ollama chat
    mock_chat.return_value = {"message": {"content": "response"}}
    # Initialize LMService with ollama provider
    service = LMService(model_provider="ollama", model_name="test_model")
    output_model = MockOutputModel()
    # Generate response using the service
    response = service.generate(prompt="test prompt", output_model=output_model)
    # Assert that the response is as expected
    assert response == "response"

# Patch the correct target for openai
@patch('lm.openai.OpenAI')
def test_generate_openai(mock_openai):
    # Mock the response of openai
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.parsed = "response"
    mock_openai.return_value.beta.chat.completions.parse.return_value = mock_response

    # Initialize LMService with openai provider
    service = LMService(model_provider="openai", model_name="test_model", api_key="test_key")
    output_model = MockOutputModel()
    # Generate response using the service
    response = service.generate(prompt="test prompt", output_model=output_model)
    # Assert that the response is as expected
    assert response == "response"
