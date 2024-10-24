# Code

The structure of the code is as follows:

There are 8 code files:
- `generate_schemas`: Runs `create` to generate schemas.
- `generate_queries`: Runs `create` to generate queries.
- `test_classifier`: Tests how well function-calling approach chooses the correct API given the synthetic query dataset.
- `create`: Creates objects.
- `llm`: Stores the `LLMService` for accessing and interfacing different LMs.
- `embed`: Stores the `EmbedService` for accessing and interfacing different embedding models.
- `models`: Stores models used, `SyntheticQuery`, `SimpleSyntheticSchema`, `ComplexSyntheticSchema`, and `FunctionClassifierTestResult`
- `optimizers`: Implements optimization algorithms to create better performing LLMs.