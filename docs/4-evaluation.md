# Evaluating Agents

### How well does GPT-4 use Weaviate to search?

We begin by studying one of the most common Agentic RAG systems, OpenAI's GPT-4o model and a Weaviate database. In this example, the Weaviate database is connected to an imaginary restaurant with 3 collections: `MenuItems`, `SupplyChain`, `Sales`

We evaluate GPT-4o on how well it selects the correct collection given a query derived from one of the collections.

For example, "How long have we served Cheeseburgers?" -> `MenuItems`, "How many burgers did we sell in March?" -> `Sales`