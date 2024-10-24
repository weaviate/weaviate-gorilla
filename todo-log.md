# ToDo

- `SimpleSchema` and `SimpleQueries` test through to evaluate simple function calling.

- run `generate_schemas.py` with `SimpleSyntheticSchema`

### Sub Components

- [ ] Add the schema example
- [ ] If result is bad, consider adding a validator that tries to create a Weaviate Collection with the schema -- if this fails, it should retry the schema generation.

- run `generate_queries.py`

- [ ] Add `weaviate_retrieval_functions`
- [ ] Generate 1 synthetic query per retrieval function per synthetic schema and envisioned use case.

- `ComplexSchema` and `ComplexQueries` to evaluate multi-hop function calling

- Test `ComplexSyntheticSchema`'s use of `@field_validator` works as an output_model
- Finishing running ^

- Test Classifier with Function Calling and Zero-Shot Classifier

== Consider changing direction based on results, otherwise ==

- Implement and Test Optimizers
- Test Optimized Function Calling
