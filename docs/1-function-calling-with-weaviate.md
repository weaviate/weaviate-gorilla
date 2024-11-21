# Function Calling with Weaviate

## Introduction

The capabilities of Large Language Models (LLMs) are being supercharged by their integration in Compound AI Systems. From Zaharia et al., a Compound AI System "tackles AI tasks using multiple interacting components, including multiple calls to models, retrievers, or external tools" [2]. Connecting AI models to external tools complements their weaknesses, such as access to continually updating data or symbolic computation. The Berkeley Function Callling Leaderboard [3] measures how well LLMs can select the correct tool to help with a task. Patil et al. further introduced the Gorilla LLM, a custom model trained on the Berkeley Function Calling Leaderboard dataset. In this work, we test an adaptation of the Gorilla LLM training and evaluation algorithms to target search database APIs.

Most examples of LLMs and database access as a tool follow an architecture inspired by Retrieval-Augmented Generation (RAG) [4]. This describes a retrieve-augment-generate pipeline that conventionally entails first sending the prompt as the search query to retrieve from a search index. The search results are then passed to an LLM to answer a question, or complete tasks more broadly. The Database Gorilla expands the capabilities of standard RAG systems to further utilize filters and result aggregations and navigate multiple data collections, in addition to search queries.

We compare the GPT-4o and GPT-4o mini LLMs on the task of choosing the correct database query API given a hypothetical information need. For example, the user query: "How many restaurants in Boston serve vegetarian dishes?" requires a boolean isVegetarian filter, a text valued "Boston" filter and a "count" aggregation on the result. Contrastively, the user query: "restaurants with seafood pasta" is sent as a search query "seafood pasta" on a text-valued description property with an associated search index. The LLM is tasked with determining which database querying APIs are necessary to answer the user query.

## Methodology

The Weaviate tool schema is implemented differently for OpenAI and Anthropic through dedicated builder functions. The process begins by calling `get_collections_info()` which connects to a Weaviate instance to retrieve metadata about available collections and their properties. This returns both a formatted description string detailing the collections and their properties, as well as a list of collection names that can be used as an enumeration. Due to token limits in function calling APIs, the description is carefully constructed to fit within 1024 tokens while maintaining all essential information about the schema.

The builder functions then construct provider-specific tool schemas - `OpenAITool` or `AnthropicTool` - each following their provider's function calling format while maintaining consistent query capabilities. The tool schemas expose a "query_database" function with parameters tailored to Weaviate's querying capabilities. The required parameter is "collection_name", which is restricted to the enumerated list of available collections. Optional parameters enable semantic search via "search_query", filtering through structured filter objects, and result aggregation using aggregation objects.

The tool schemas use structured Pydantic models to represent filters and aggregations, providing strong type validation and clear parameter boundaries. For filtering, the schema supports IntPropertyFilter, TextPropertyFilter, and BooleanPropertyFilter models. Numeric filters must specify a property name, comparison operator (=, <, >, <=, >=), and numeric value. Text filters support equality and LIKE operators, while boolean filters handle true/false comparisons. For aggregations, the schema uses IntAggregation, TextAggregation, and BooleanAggregation classes that enforce valid statistical operations for each data type - such as MIN, MAX, MEAN for numbers or TOP_OCCURRENCES for text. Additionally, grouping operations are supported through a GroupBy model that specifies the property to group results by.

This structured approach ensures that LLMs can only construct valid Weaviate queries by providing awareness of available collections and their properties, comprehensive querying features through strongly-typed models, and built-in validation of all query parameters. The implementation has been thoroughly tested with both GPT-4 and Claude models, demonstrating robust performance in translating natural language queries into valid Weaviate operations.

## Future

Several promising directions could extend this work:

1. **Ollama Integration**: The `OllamaTool` implementation would enable local deployment of database query translation, reducing latency and costs while maintaining privacy. This could leverage smaller, specialized models trained specifically for database operations.

2. **DSL vs Structured Models**: Comparing the effectiveness of generating Domain Specific Language (DSL) strings versus structured model objects could reveal tradeoffs in accuracy and flexibility. DSL generation might be more natural for LLMs but could introduce more errors, while structured models provide stronger guarantees but may be more constraining.

3. **Multi-Step Query Planning**: Extending the system to handle complex queries requiring multiple steps or joins between collections. This would involve teaching LLMs to break down complex information needs into sequences of simpler queries.

4. **Schema-Aware Fine-Tuning**: Creating specialized models fine-tuned on specific database schemas could improve accuracy for domain-specific applications while reducing model size and inference costs.

5. **Query Optimization**: Incorporating query performance metrics to train models to generate not just correct but efficient queries, considering factors like index usage and execution plans.

6. **Cross-Database Compatibility**: Expanding beyond Weaviate to support multiple database systems, potentially creating a unified query interface that can target different backends.

These developments would push forward the integration of LLMs with database systems, making natural language interfaces to databases more powerful and practical for real-world applications.