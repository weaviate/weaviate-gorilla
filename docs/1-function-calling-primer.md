# 1. Function Calling Primer

The capabilities of LLMs can be extended by connecting them to external computation, also referred to as tools. The most common tool Agents are connected to are database querying APIs. This connection is often referred to as Agentic RAG (Retrieval-Augmented Generation).

Agentic RAG offers two quick benefits over standard RAG systems. Whereas a RAG system typically uses the prompt as a search query, an Agent writes a search query for the particular information need. Imagine the user tells a long story about their day, interleaved with questions for the chatbot. An Agentic RAG system can parse out these information-seeking queries such as "vitamin D health benefits" or "emails from today".

Further, whereas RAG systems typically run a single search before generation, Agents can decide to search again. Agents can also parallelize these search queries and corresponding requests. The user asks "Compare the nutritional benefits of quinoa, brown rice, and barley". The Agent can then simultaneously search for the nutritional benefits of quinoa, brown rice, and barley as 3 separate search queries. The Agent then generates a response using the context retrieved from all 3 queries.

The next steps for Agents and Weaviate are to connect Agents to Weaviate's APIs for Select and Aggregate style functionality. This is similar to SQL APIs.

The core steps to implementing Agentic RAG are:
1. Connect to a Weaviate Instance
2. Define the Search Function
3. Define the Function Schema
4. Send the Function Schema, in addition to the prompt, to the LLM
5. In the runtime of the LLM, write a mapping from Function name to Function execution
6. Loop to check if the Agent selected to finish the response or call the function.

