## `/Create`

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