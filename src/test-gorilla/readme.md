# Testing Philosophy

Broadly put, test scripts in research repositories are designed to compare algorithm A with algorithm B.

This starts simple, but as the nuances of algorithms A and B are explored further, the configuration details can evolve rapidly.

Thus we try to jointly unify testing scripts in a single file, as well as individual tests. This facilitates the evolution of testing.

### Ablations
- Required `tool_rationale` argument
- Toggle `parallel_tool_calls` in LLM SDK
- Tool per Collection
- Structured Output Tool Calls