# Function Calling Primer

The capabilities of LLMs can be extended by connecting them to external computation, also referred to as tools. The most common tool used in Agents are databases. Agentic RAG offers two quick benefits over standard RAG systems. Whereas a RAG system typically uses the prompt as a search query, an Agent writes a search query for the particular information need. Further, whereas RAG systems typically run a single search before generation, Agents can decide to search again. Agents can also parallelize these search queries and corresponding requests. The next steps for Agents and Weaviate are to connect Agents to Weaviate's APIs for Select and Aggregate style functionality from SQL.

The core steps to implementing Agentic RAG are:
1. Setup a Weaviate Instance
2. Define the Function Schema
3. In the runtime of the LLM, write a mapping from Function name to Function execution
4. Send the Function Schema in addition to the prompt to the LLM
5. Loop to check if the Agent selected to finisht the response or call the function.

The easiest way to interface tools to LLMs is through APIs or functions. These functions are typically defined in the runtime of the agent.

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