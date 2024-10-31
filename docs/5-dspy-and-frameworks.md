# 5. DSPy and Agent Frameworks

In addition to LLM APIs, such as the OpenAI, Claude, Gemini, Ollama, or vLLM SDKs, it is also common to use LLM frameworks to orchestrate inference. At Weaviate, we have worked with and recommend many of these frameworks such as: DSPy, LangChain, Crew AI, LlamaIndex, and Letta. These frameworks have also made incredible efforts in integration engineering, for example please see this notebook on using [LangChain and DSPy together](https://github.com/stanfordnlp/dspy/blob/main/examples/tweets/compiling_langchain.ipynb).

As mentioned, many of these frameworks implement a `Tool` model that is then integrated with the abstractions of the respective framework. Although there is significant overlap in functionality per framework, there are also quite a few interesting novelties to highlight. For example, DSPy uses the `Tool` model to interface automated prompt engineering algorithms with the descriptions of tools. Crew AI novely combines multi-agent persona systems with functions.

### DSPy quick reference:

```python
from dspy.predict.avatar import Tool, Avatar

Tool(
    tool: search_docs,
    name: "Search Code Documentation",
    desc: "The documentation for the DSPy Python package, contains helpful code references and conceptual explanations.",
    input_type: str
)
```