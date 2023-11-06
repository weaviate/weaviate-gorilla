# DataEngine
The DataEngine is used to store, generate, and verify synthetic training examples to train the Gorilla to translate from natural language text into Weaviate's GraphQL Search APIs.

There are 3 main parts to this, the `initEngine` which creates an initial set of synthetic queries which are then validated in the `validatorEngine`, we then try to fix queries that failed to execute in the `retryEngine`. The flow of functions is shown in the following illustration:

<img width="1031" alt="WeaviateGorillaDataEngine" src="https://github.com/weaviate/Auto/assets/25864937/60e3a1c2-a557-4866-82d3-bfaaea7ec623">
<br /><br />

The `data` folder is the storage used for all datasets.

The Knowledge Base and Task Examples live in the Data Folder.

`utils` contains misc. tools for dataset development:
