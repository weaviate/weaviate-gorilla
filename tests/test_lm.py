import pytest
from unittest.mock import Mock, patch, MagicMock
from src.lm.lm import LMService, LMModelProvider
from src.models import TestLMConnectionModel
from src.utils.weaviate_fc_utils import OpenAITool

# Fixtures for different model providers
@pytest.fixture
def mock_openai():
    with patch('openai.OpenAI') as mock:
        # Mock the chat completion response
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content="Hello!",
                    tool_calls=None,
                    parsed=Mock(generic_response="Hello!")
                )
            )
        ]
        mock_instance = mock.return_value
        mock_instance.chat.completions.create.return_value = mock_response
        mock_instance.beta.chat.completions.parse.return_value = mock_response
        yield mock

@pytest.fixture
def mock_anthropic():
    with patch('anthropic.Anthropic') as mock:
        # Mock the messages response
        mock_response = Mock()
        mock_response.content = [Mock(text="Hello!")]
        mock_response.stop_reason = None
        mock_instance = mock.return_value
        mock_instance.messages.create.return_value = mock_response
        yield mock

@pytest.fixture
def mock_cohere():
    with patch('cohere.ClientV2') as mock:
        mock_instance = mock.return_value
        mock_instance.chat.return_value = "Hello!"
        yield mock

@pytest.fixture
def mock_ollama():
    with patch('ollama') as mock:
        mock.chat.return_value = {
            "message": {
                "content": "Hello!",
                "tool_calls": None
            }
        }
        yield mock

# Test initialization for different providers
def test_openai_init(mock_openai):
    service = LMService("openai", "gpt-4o", "test-key")
    assert service.model_provider == "openai"
    assert service.model_name == "gpt-4"
    mock_openai.assert_called_once_with(api_key="test-key")

def test_anthropic_init(mock_anthropic):
    service = LMService("anthropic", "claude-sonnet-3.5", "test-key")
    assert service.model_provider == "anthropic"
    assert service.model_name == "claude-3"
    mock_anthropic.assert_called_once_with(api_key="test-key")

def test_gemini_init(mock_openai):
    service = LMService("openai", "gemini-1.5-pro", "test-key")
    assert service.model_provider == "openai"
    assert service.model_name == "gemini-1.5-pro"
    mock_openai.assert_called_once_with(
        api_key="test-key",
        base_url="https://generativelanguage.googleapis.com/v1beta/"
    )

# Test generate method
def test_openai_generate(mock_openai):
    service = LMService("openai", "gpt-4", "test-key")
    response = service.generate("Say hello")
    assert response == "Hello!"
    mock_openai.return_value.chat.completions.create.assert_called_once()

def test_openai_generate_with_output_model(mock_openai):
    service = LMService("openai", "gpt-4", "test-key")
    response = service.generate("Say hello", TestLMConnectionModel)
    assert response.generic_response == "Hello!"
    mock_openai.return_value.beta.chat.completions.parse.assert_called_once()

def test_anthropic_generate(mock_anthropic):
    service = LMService("anthropic", "claude-3", "test-key")
    response = service.generate("Say hello")
    assert response == "Hello!"
    mock_anthropic.return_value.messages.create.assert_called_once()

# Test function calling
def test_openai_function_calling(mock_openai):
    # Mock tool calls response
    mock_openai.return_value.chat.completions.create.return_value.choices[0].message.tool_calls = [
        Mock(
            function=Mock(
                name="test_function",
                arguments='{"arg": "value"}'
            )
        )
    ]
    
    service = LMService("openai", "gpt-4", "test-key")
    tools = [OpenAITool(
        type="function",
        function={
            "name": "test_function",
            "description": "A test function",
            "parameters": {"type": "object", "properties": {"arg": {"type": "string"}}}
        }
    )]
    
    response = service.one_step_function_selection_test("Use the test function", tools)
    assert response is not None
    assert response[0].function.arguments == '{"arg": "value"}'

def test_anthropic_function_calling(mock_anthropic):
    # Mock tool use response
    mock_anthropic.return_value.messages.create.return_value.stop_reason = "tool_use"
    mock_anthropic.return_value.messages.create.return_value.content = [
        Mock(
            type="tool_use",
            name="test_function",
            input={"arg": "value"}
        )
    ]
    
    service = LMService("anthropic", "claude-3", "test-key")
    tools = [OpenAITool(
        type="function",
        function={
            "name": "test_function",
            "description": "A test function",
            "parameters": {"type": "object", "properties": {"arg": {"type": "string"}}}
        }
    )]
    
    response = service.one_step_function_selection_test("Use the test function", tools)
    assert response == {"arg": "value"}

# Test error handling
def test_invalid_provider():
    with pytest.raises(ValueError, match="Unsupported model provider: invalid"):
        LMService("invalid", "model", "test-key")

# Test structured outputs
def test_openai_structured_outputs(mock_openai):
    mock_openai.return_value.beta.chat.completions.parse.return_value.choices[0].message.parsed = Mock(
        use_tools=True,
        tool_calls={"function": "test", "arguments": {"arg": "value"}}
    )
    
    service = LMService("openai", "gpt-4", "test-key")
    tools = [OpenAITool(
        type="function",
        function={
            "name": "test_function",
            "description": "A test function",
            "parameters": {"type": "object", "properties": {"arg": {"type": "string"}}}
        }
    )]
    
    response = service.call_tools_with_structured_outputs("Use the test function", tools)
    assert response == {"function": "test", "arguments": {"arg": "value"}}