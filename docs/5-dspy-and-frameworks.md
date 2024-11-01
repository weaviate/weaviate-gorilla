# 5. Agent Frameworks

In addition to LLM APIs, such as the OpenAI, Claude, Gemini, Ollama, or vLLM SDKs, it is also common to use LLM frameworks to orchestrate inference. At Weaviate, we have worked with and recommend many of these frameworks such as: DSPy, LangChain, Crew AI, LlamaIndex, and Letta. These frameworks have also made incredible efforts in integration engineering, for example please see this notebook on using [LangChain and DSPy together](https://github.com/stanfordnlp/dspy/blob/main/examples/tweets/compiling_langchain.ipynb).

As mentioned, many of these frameworks implement a `Tool` model that is then integrated with the abstractions of the respective framework. Although there is significant overlap in functionality per framework, there are also quite a few interesting novelties to highlight. For example, DSPy uses the `Tool` model to interface automated prompt engineering algorithms with the descriptions of tools, such as [AvaTaR](https://arxiv.org/abs/2406.11200). Crew AI novely combines multi-agent persona systems with functions.

```python
# CrewAI
# Instantiate tools
docs_tool = DirectoryReadTool(directory='./blog-posts')
file_tool = FileReadTool()
search_tool = SerperDevTool()
web_rag_tool = WebsiteSearchTool()

# Create agents
researcher = Agent(
    role='Market Research Analyst',
    goal='Provide up-to-date market analysis of the AI industry',
    backstory='An expert analyst with a keen eye for market trends.',
    tools=[search_tool, web_rag_tool],
    verbose=True
)
```

```python
# LangChain Default Tools
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
tool = WikipediaQueryRun(api_wrapper=api_wrapper)
tool.run({"query": "langchain"})
```

LlamaIndex has `QueryEngineTool` differentiated from `FunctionTool`. More information can be found [here](https://docs.llamaindex.ai/en/stable/module_guides/deploying/agents/tools/).

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

![Weaviate Gorilla](../visuals/avatar/avatar-1.png)