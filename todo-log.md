# ToDo

## Search Queries need to reflect their unique application

For example, `Find dishes that are vegetarian and sort them by price` is not a search query.

## Aggregation String Parser

## Vector Distance for AST scoring of ground truth and predicted query

Or just, is there a search query...

## Cleanup

Standardize how query datasets are created.

- Collection Router per Collection => Search Query
- Synthetic Filters
- Synthetic Aggregations (missing GroupBy)

Generate query combination datasets:
- Search + Filters
- Search + Aggregations
- Filters + Aggregations
- Search + Filters + Aggregations

Get more detailed about evaluation.
- Binary accuracy -- is everything correct?
- Abstract Syntax Tree matching -- how does this work?

Ablations
- GPT-4o vs. Llama 3.2B
- Parallel Function Calling
- Rationale as a required argument

## Optimized Function Calling with AvaTaR

- Implement and Test Optimizers
- Test Optimized Function Calling

## Debt

- Make Aggregate syntax description more succinct.

- Bug with Filtering on `date` properties (tries to cast the date to a float with the `>`, etc. operators)

- Need a more compact representation of the collections in Weaviate to optimize the tool description (1024 token limit).

- Revise thinking around `Simple-` and `Complex-` Schema. Both should use the `WeaviateCollectionConfig` model but with different prompts.

- Test ReAct-style thinking and function calling as a required argument

# === Somewhat finished ===

## Schema Generation

[X] Tested Schema Generation

`SimpleSchema` and `SimpleQueries` test through to evaluate simple function calling.

Run `generate_schemas.py` to generate 50 synthetic schemas

Then run `clean_up_schemas.py`

[X] FIX! these are missing `vectorizer` / `vectorIndexConfig` (which you need to create a class by sending a schema in a post request)
[X] Well... `class` is of course a reserved keyword... so need to rename with file saving

- Works fairly well, but could benefit from diverse generation and deduplication strategies

[X] Implement Skeleton of Deduplication in `Create`
[X] Test Brute Force History Deduplication
[--] Test Last K History Deduplication
[--] Test Generate, Retrieve, and Mark Duplicate Deduplication


## Basic Weaviate Function Calling

[X] Get Weaviate Collections from Meta API
[X] Parse into Collections
[X] Parse into Tools per Collection
[X] Test with 1 query
[X] Add Function Calling to LMService

```python
Tool(
    type="function",
    function=Function(
        name="search_weaviate_collection",
        description="Optimize me with DSPy",
        parameters=Parameters(
            type="object",
            properties={
                "collection_name": ParameterProperty(
                    type="string",
                    description="Optimize me with DSPy"
                ),
                "search_query": ParameterProperty(
                    type="string",
                    description="Optimize me with DSPy"
                ),
                "filter_string": ParameterProperty(
                    type="string",
                    description="{filter_string_dsl} + Optimize me with DSPy"
                ),
                "aggregation_string": ParameterProperty(
                    type="string",
                    description="{aggregation_string_dsl} + Optimize me with DSPy"
                )
            },
            required=["collection_name"]
        )
    )
)
```

## Testing Function Calling

- Test Classifier with Function Calling and Zero-Shot Classifier

with Collection Routing Evaluation:

Given 3 collections, generate a query that should be routed to each.

GPT-4o vs. Llama 3.2 (Llama not tested)

Need to consider how Parallel Function Calling impacts this evaluation methodology.

## Where Filter DSL

Given a collection, generate a filter seeking query for each property.

Note, each collection contains 1 TEXT property, 1 NUMBER property, and 1 BOOLEAN property.

Note, evaluation entanglement with collection selection.

## Test Filter DSL as a Function Calling Argument