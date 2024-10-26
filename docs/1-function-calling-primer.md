# Function Calling Primer

The capabilities of LLMs can be extended by connecting them to external computation, also referred to as tools.

The easiest way to interface tools to LLMs is through APIs or functions.

These functions are typically defined in the runtime of the agent.

In order to prompt the agent with the tools it has access to, the AI industry has settled on the `function calling` schema.

Here is a Pydantic Model defining this:

```python
class ParameterProperty(BaseModel):
    type: str
    description: str

class Parameters(BaseModel):
    type: Literal["object"]
    properties: Dict[str, ParameterProperty]
    required: Optional[List[str]]

class Function(BaseModel):
    name: str
    description: str
    parameters: Parameters

class Tool(BaseModel):
    type: Literal["function"]
    function: Function
```

This is the standard tool schema that LLM APIs such as OpenAI, Anthropic, Gemini, Ollama, and vLLM use, to name a few.