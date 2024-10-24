"""
# Run with:

`python3 -m unittest test_lm.py`

"""

import unittest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel
from lm import LMService, LMModelProvider

class MockOutputModel(BaseModel):
    def model_dump_json(self):
        return '{"key": "value"}'

class TestLMService(unittest.TestCase):

    @patch('ollama')
    @patch('openai.OpenAI')
    def test_init_ollama(self, mock_openai, mock_ollama):
        service = LMService(model_provider="ollama", model_name="test_model")
        self.assertEqual(service.model_provider, "ollama")
        self.assertEqual(service.lm_client, mock_ollama)

    @patch('ollama')
    @patch('openai.OpenAI')
    def test_init_openai(self, mock_openai, mock_ollama):
        mock_openai_instance = mock_openai.return_value
        service = LMService(model_provider="openai", model_name="test_model", api_key="test_key")
        self.assertEqual(service.model_provider, "openai")
        self.assertEqual(service.lm_client, mock_openai_instance)

    @patch('ollama.chat')
    def test_generate_ollama(self, mock_chat):
        mock_chat.return_value = {"message": {"content": "response"}}
        service = LMService(model_provider="ollama", model_name="test_model")
        output_model = MockOutputModel()
        response = service.generate(prompt="test prompt", output_model=output_model)
        self.assertEqual(response, "response")

    @patch('openai.OpenAI')
    def test_generate_openai(self, mock_openai):
        mock_response = MagicMock()
        mock_response.choices[0].message.parsed = "response"
        mock_openai.return_value.beta.chat.completions.parse.return_value = mock_response
        service = LMService(model_provider="openai", model_name="test_model", api_key="test_key")
        output_model = MockOutputModel()
        response = service.generate(prompt="test prompt", output_model=output_model)
        self.assertEqual(response, "response")

if __name__ == '__main__':
    unittest.main()