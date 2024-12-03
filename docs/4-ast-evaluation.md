# AST Evaluation

## Introduction

When evaluating how well language models translate natural language into database queries, a simple boolean metric assessing if the predicted query is identical to the ground truth query provides limited insight into partial successes. We need an evaluation approach that can measure how much of the query structure was correctly generated, even if some components were incorrect. We use Abstract Syntax Tree (AST) evaluation to assess the structural matching between predicted and ground truth queries in our experiments. The AST approach breaks down queries into their hierarchical components - starting with the target collection as the root node, followed by branches for search queries, filters, aggregations, and grouping operations. Each component is evaluated for exact matches, with the collection match being required for any points to be awarded.

In our experiments, AST evaluation helps measure how well language models can translate natural language queries into structured Weaviate API calls through a weighted scoring system. The scoring heavily weights getting the target collection correct (40% of total score), as this is fundamental to query correctness. The remaining score is evenly distributed (15% each) across matching the search query text, filter specifications, aggregation operations, and grouping property. This hierarchical scoring approach allows us to quantify partial successes in query generation and identify specific areas where models struggle.

## Methodology

The AST evaluation methodology employs a comprehensive weighted scoring system to assess query similarity. The largest weight (40%) is assigned to correctly matching the target collection, which is considered fundamental - mismatching collections results in a score of 0. The remaining 60% is evenly distributed (15% each) across four components: search queries, which require exact case-insensitive text matches; filters, which evaluate property names, operators and values across integer, text and boolean types; aggregations, which check property names and metrics across different types; and group by operations, which require exact property name matches. Each component's score is averaged across its subtypes when present, and the final score ranges from 0.0 to 1.0, with 1.0 indicating perfect structural alignment across all elements.

## Future Work

Several opportunities exist to enhance the AST evaluation approach:

1. Semantic Equivalence
   - Current implementation requires exact matches for property names and values
   - Could incorporate semantic similarity measures for text values
   - Could recognize equivalent but differently expressed numeric conditions

2. Order-Independence
   - Add support for matching queries where components appear in different orders but are logically equivalent
   - Particularly relevant for multiple filters or aggregations

3. Partial Credit Scoring
   - Implement more granular scoring for partial matches in filters and aggregations
   - Consider fuzzy matching for property names to handle minor typos or variations

4. Query Optimization Awareness
   - Recognize when a predicted query is more efficient but logically equivalent
   - Award bonus points for more optimal query structures

5. Cross-Collection Query Support
   - Extend evaluation to handle queries spanning multiple collections
   - Develop scoring for join operations and cross-references