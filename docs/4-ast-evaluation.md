# AST Evaluation

## Introduction

Abstract Syntax Tree (AST) evaluation is a technique used to assess the structural similarity between predicted and ground truth Weaviate queries in our experiments. Rather than using exact string matching, AST evaluation compares queries by analyzing their hierarchical components and structure. This approach is particularly valuable for evaluating language model outputs because it can capture semantic equivalence even when the surface syntax differs.

In our experiments, AST evaluation helps measure how well language models can translate natural language queries into structured Weaviate API calls. The scoring system prioritizes getting fundamental elements correct (like the target collection) while also considering the accuracy of more detailed query components like filters, aggregations, and grouping.

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