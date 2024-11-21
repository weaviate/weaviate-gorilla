[Compiled from `format-introduction.py]

The capabilities of Large Language Models (LLMs) are being supercharged by their integration in Compound AI Systems. From Zaharia et al., a Compound AI System "tackles AI tasks using multiple interacting components, including multiple calls to models, retrievers, or external tools" [2]. Connecting AI models to external tools complements their weaknesses, such as access to continually updating data or symbolic computation. The Berkeley Function Callling Leaderboard [3] measures how well LLMs can select the correct tool to help with a task. Patil et al. further introduced the Gorilla LLM, a custom model trained on the Berkeley Function Calling Leaderboard dataset. In this work, we test an adaptation of the Gorilla LLM training and evaluation algorithms to target search database APIs.

Most examples of LLMs and database access as a tool follow an architecture inspired by Retrieval-Augmented Generation (RAG) [4]. This describes a retrieve-augment-generate pipeline that conventionally entails first sending the prompt as the search query to retrieve from a search index. The search results are then passed to an LLM to answer a question, or complete tasks more broadly. The Database Gorilla expands the capabilities of standard RAG systems to further utilize filters and result aggregations and navigate multiple data collections, in addition to search queries.

We compare the GPT-4o and GPT-4o mini LLMs on the task of choosing the correct database query API given a hypothetical information need. For example, the user query: "How many restaurants in Boston serve vegetarian dishes?" requires a boolean isVegetarian filter, a text valued "Boston" filter and a "count" aggregation on the result. Contrastively, the user query: "restaurants with seafood pasta" is sent as a search query "seafood pasta" on a text-valued description property with an associated search index. The LLM is tasked with determining which database querying APIs are necessary to answer the user query.

The synthetic database schemas were generated to create realistic test cases for evaluating LLM query capabilities. Each schema set represents a different business domain with three interconnected collections, carefully designed to enable semantic search and complex querying patterns. The schemas provide a foundation for testing how well LLMs can understand database structures and generate appropriate queries based on natural language requests.

To evaluate the ability of large language models (LLMs) to translate natural language queries into structured Weaviate API calls, we needed a comprehensive test dataset that covered diverse combinations of Weaviate's core query capabilities. These capabilities include semantic search queries for finding relevant results based on natural language understanding, property filters for exact matching on integer, text, and boolean fields, aggregations for computing statistics over integer, text, and boolean properties, and grouping operations to segment results by property values. Rather than manually writing test cases, we developed a systematic approach to generate synthetic queries that exercise these capabilities across different database schemas. This systematic approach allowed us to test the full range of Weaviate's query functionality, evaluate LLM performance across different query complexity levels, assess generalization across multiple database schemas, and create a large enough dataset for meaningful statistical analysis.

Abstract Syntax Tree (AST) evaluation is a technique used to assess the structural similarity between predicted and ground truth Weaviate queries in our experiments. Rather than using exact string matching, AST evaluation compares queries by analyzing their hierarchical components and structure. This approach is particularly valuable for evaluating language model outputs because it can capture semantic equivalence even when the surface syntax differs.

In our experiments, AST evaluation helps measure how well language models can translate natural language queries into structured Weaviate API calls. The scoring system prioritizes getting fundamental elements correct (like the target collection) while also considering the accuracy of more detailed query components like filters, aggregations, and grouping.