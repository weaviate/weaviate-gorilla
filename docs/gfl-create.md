## Notes on gfl's `/Create` API while developing the Weaviate Gorilla

General concept of:

If uuids:
    for each object:
        generate `num_samples` new objects based on the `instruction`
        do something about deduplication of the samples
else:
    generate `num_samples` new objects based on the `instruction`
    do something about deduplication of the samples

If no uuids are given, create from scratch.

```python
gfl.create(
    collection="Schemas",
    instructions=f"""
    Write a synthetic database schema such as the following example:
    
    [[ database schema ]]
    {example_database_schema}

    With the following envisioned use case

    [[ use case ]]
    {use_case}
    """,
    num_samples=50,
    on_properties=[
        "schema",
        "use_case"
    ]
)
```

# Deduplication of Samples

### Brute Force History

Provide the LLM with all samples generated so far. Perhaps works for long context LLMs and / or small GFL tasks.

Each Schema is **500 tokens** so this doesn't scale that well.

### Last K History

Provide the LLM with the last K samples generated.

### Generate, Retry

Generate then provide the new sample with the top K similar examples determined from a search. Task the LLM to mark duplicates with a boolean-valued output.

### Clustering-based Deduplication

Cluster generated samples with vector embeddings. Deduplicate if distance between vectors is less than a threshold, t.

# Creating from a previous Collection (Create Checkpointing)

Let's say I generate 50 schemas and then want to generate another 50...

Now the deduplication needs to be more stateful, thinking GRAD (Generate, then Retrieve and Assess Duplicates) is the leading philosophy for this.