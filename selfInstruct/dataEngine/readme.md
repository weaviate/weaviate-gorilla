## Weaviate Gorilla Data Engine!

There are 5 main parts to this:

- data
- initEngine
- retryEngine
- trainTestSplitter
- validatorEngine
- syntheticSchemaWriter

The Knowledge Base and Task Examples live in the Data Folder.

We kick things off with the initEngine, which creates synthetic queries.

We test if these queries work in the validatorEngine.

If not, we fix them with the retryEngine.

When we want to increase our dataset size, we use the syntheticSchemaWriter to add more schemas.

When we are ready for modeling, we use the trainTestSplitter.
