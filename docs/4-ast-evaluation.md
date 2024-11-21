# AST Evaluation

## Introduction

Abstract Syntax Tree (AST) evaluation is a technique used to assess the structural similarity between predicted and ground truth Weaviate queries in our experiments. Rather than using exact string matching, AST evaluation compares queries by analyzing their hierarchical components and structure. This approach is particularly valuable for evaluating language model outputs because it can capture semantic equivalence even when the surface syntax differs.

In our experiments, AST evaluation helps measure how well language models can translate natural language queries into structured Weaviate API calls. The scoring system prioritizes getting fundamental elements correct (like the target collection) while also considering the accuracy of more detailed query components like filters, aggregations, and grouping.

## Methodology

The AST evaluation methodology assigns weighted scores to different components of the Weaviate query structure:

1. Root Node (Collection) - 40% of total score
   - The target_collection must match exactly
   - If collections don't match, the entire score is 0 since this represents a fundamental misunderstanding

2. Search Query - 15% of total score
   - Exact text match of search queries (case-insensitive)
   - Full points if both queries have matching search terms or both have no search terms

3. Filters - 15% of total score
   - Evaluates matches across integer, text, and boolean filters
   - For each filter type, checks:
     - Property name match
     - Operator match
     - Value match
   - Score is averaged across all filter types present

4. Aggregations - 15% of total score
   - Evaluates matches across integer, text, and boolean aggregations
   - For each aggregation type, checks:
     - Property name match
     - Metrics match
   - Score is averaged across all aggregation types present

5. Group By - 15% of total score
   - Exact match of groupby property names

The final score ranges from 0.0 to 1.0, where 1.0 represents a perfect structural match across all components.

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