# ToDo

[NEXT MILESTONE]

`SimpleSchema` and `SimpleQueries` test through to evaluate simple function calling.

[CODE IS RUNNING] run `generate_schemas.py` to generate 50 synthetic schemas

[DEDUPLICATION IS NEEDED]

[IN DEVELOPMENT] run `generate_queries.py` to generate 8 x 50 = 400 synthetic queries

- [ ] Add `weaviate_retrieval_functions`
- [ ] Generate 1 synthetic query per retrieval function per synthetic schema and envisioned use case.

- `ComplexSchema` and `ComplexQueries` to evaluate multi-hop function calling

- Test `ComplexSyntheticSchema`'s use of `@field_validator` works as an output_model
- Finishing running ^

- Test Classifier with Function Calling and Zero-Shot Classifier

== Consider changing direction based on results, otherwise ==

- Implement and Test Optimizers
- Test Optimized Function Calling

# Debt

- Revise thinking around `Simple-` and `Complex-` Schema. Both should use the `WeaviateCollectionConfig` model but with different prompts.