# Function Calling with Weaviate

## Introduction

The capabilities of Large Language Models (LLMs) are being supercharged by their integration in Compound AI Systems. From Zaharia et al., a Compound AI System “tackles AI tasks using multiple interacting components, including multiple calls to models, retrievers, or external tools” [2]. Connecting AI models to external tools complements their weaknesses, such as access to continually updating data or symbolic computation. The Berkeley Function Callling Leaderboard [3] measures how well LLMs can select the correct tool to help with a task. Patil et al. further introduced the Gorilla LLM, a custom model trained on the Berkeley Function Calling Leaderboard dataset. In this work, we present the Database Gorilla, an adaptation of the Gorilla LLM training and evaluation algorithms to target database APIs.

Most examples of LLMs and database access as a tool follow an architecture inspired by Retrieval-Augmented Generation (RAG) [4]. This describes a retrieve-augment-generate pipeline that conventionally entails first sending the prompt as the search query to retrieve from a search index. The search results are then passed to an LLM to answer a question, or complete tasks more broadly. The Database Gorilla expands the capabilities of standard RAG systems to further utilize filters and result aggregations and navigate multiple data collections, in addition to search queries.

We compare the GPT-4o and GPT-4o mini LLMs on the task of choosing the correct database query API given a hypothetical information need. For example, the user query: “How many restaurants in Boston serve vegetarian dishes?” requires a boolean isVegetarian filter, a text valued “Boston” filter and a “count” aggregation on the result. Contrastively, the user query: “restaurants with seafood pasta” is sent as a search query “seafood pasta” on a text-valued description property with an associated search index. The LLM is tasked with determining which database querying APIs are necessary to answer the user query.

## Methodology

## Future