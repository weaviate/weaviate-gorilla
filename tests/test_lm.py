# tests/test_lm.py

import pytest
from unittest.mock import patch

# Adjust the import path if your lm.py is in a different location
from src.lm.lm import LMService


@pytest.mark.parametrize("provider, model_name", [
    ("ollama", "llama3.1:8b"),
    ("openai", "gpt-3.5-turbo"),
    ("anthropic", "claude-v1.3"),
    ("cohere", "command-medium-nightly"),
    ("together", "together-gpt-j-6B"),
])
def test_lmservice_initialization(provider, model_name):
    """
    Tests that the LMService can be created for each provider
    without raising an exception.
    """
    # We don't want to make a real API call during __init__,
    # so we'll patch the connection_test method:
    with patch.object(LMService, "connection_test", return_value=None):
        service = LMService(model_provider=provider, model_name=model_name)
        assert service.model_provider == provider
        assert service.model_name == model_name


@patch("ollama.chat", autospec=True)
def test_generate_ollama(mock_ollama_chat):
    """
    Tests LMService.generate() for the 'ollama' provider
    by mocking the ollama.chat function.
    """
    # Fake response that the Ollama chat API might return
    mock_ollama_chat.return_value = {
        "message": {
            "content": "Hello from Ollama mock!"
        }
    }

    # Again, patch out connection_test to avoid real calls
    with patch.object(LMService, "connection_test", return_value=None):
        service = LMService(model_provider="ollama", model_name="llama3.1:8b")

    # Now, call .generate() and verify the return
    response = service.generate("Just checking!")
    assert response == "Hello from Ollama mock!", (
        "generate() should return the mocked content from ollama.chat"
    )


@patch("openai.OpenAI.chat.completions.create", autospec=True)
def test_generate_openai(mock_create):
    """
    Tests LMService.generate() for the 'openai' provider
    by mocking the openai.OpenAI API call.
    """
    # Simulate OpenAI's chat.completions.create response structure
    mock_create.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Mocked OpenAI response!"
                }
            }
        ]
    }

    with patch.object(LMService, "connection_test", return_value=None):
        service = LMService(model_provider="openai", model_name="gpt-3.5-turbo")

    result = service.generate("Hello there!")
    assert result == "Mocked OpenAI response!", "Should return the mocked OpenAI response"


def test_invalid_provider():
    """
    Tests that an invalid provider string raises ValueError.
    """
    with pytest.raises(ValueError) as excinfo:
        with patch.object(LMService, "connection_test", return_value=None):
            LMService(model_provider="not-a-real-provider", model_name="dummy-model")

    assert "Unsupported model provider" in str(excinfo.value)
