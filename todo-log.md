# ToDo

[IN DEVELOPMENT]

[X] Tested Schema Generation

`SimpleSchema` and `SimpleQueries` test through to evaluate simple function calling.

Run `generate_schemas.py` to generate 50 synthetic schemas

- Works fairly well, but could benefit from diverse generation and deduplication strategies

[ ] Test Brute Force History Deduplication
[ ] Test Last K History Deduplication
[ ] Test Generate, Retrieve, and Mark Duplicate Deduplication

[IN DEVELOPMENT] run `generate_queries.py` to generate 8 x 50 = 400 synthetic queries

[X] Get Weaviate Collections from Meta API
[X] Parse into Collections
[ ] Parse into Tools per Collection
[ ] Test with 1 query
[ ] (Optionally) Then abstract this into a connection test for the LLMs


- Requires re-think of function calling with Weaviate

## FINE-GRAINED FUNCTION SET PER COLLECTION`
1. Parses Weaviate Schemas with a meta API
2. Creats 8 Specific Tools for each of the collections

8 Specific Tools
1. Search
2. Filters (no search)
3. Search + Filters
4. Agggregate TEXT
5. Aggregate NUMBER
6. Aggregate BOOLEAN
7. Count Objects
8. Groupby Property

## FUNCTION SET PER COLLECTION
1. Parses Weaviate Schemas with a meta API
2. Creates 1 General Tool for each of the collections

This requires an AST parser for the function calling arguments.

## FUNCTION SET FOR MULTIPLE COLLECTIONS
1. Add Weaviate Schema to description
2. 1 Very General Tool for all of Weaviate Search

- [ ] Generate 1 synthetic query per retrieval function per synthetic schema and envisioned use case.

===
- `ComplexSchema` and `ComplexQueries` to evaluate multi-hop function calling

- Test `ComplexSyntheticSchema`'s use of `@field_validator` works as an output_model
- Finishing running ^

- Test Classifier with Function Calling and Zero-Shot Classifier

== Consider changing direction based on results, otherwise ==

- Implement and Test Optimizers
- Test Optimized Function Calling

# Debt

- Revise thinking around `Simple-` and `Complex-` Schema. Both should use the `WeaviateCollectionConfig` model but with different prompts.