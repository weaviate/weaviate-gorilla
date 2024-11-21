# Synthetic Weaviate Queries

## Introduction

To evaluate the ability of large language models (LLMs) to translate natural language queries into structured Weaviate API calls, we needed a comprehensive test dataset. This dataset needed to cover diverse combinations of Weaviate's core query capabilities:

- Semantic search queries for finding relevant results based on natural language understanding
- Property filters for exact matching on integer, text, and boolean fields
- Aggregations for computing statistics over integer, text, and boolean properties 
- Grouping operations to segment results by property values

Rather than manually writing test cases, we developed a systematic approach to generate synthetic queries that exercise these capabilities across different database schemas. This allowed us to:

1. Test the full range of Weaviate's query functionality
2. Evaluate LLM performance across different query complexity levels
3. Assess generalization across multiple database schemas
4. Create a large enough dataset for meaningful statistical analysis

## Methodology

The query generation process follows these key steps:

1. **Schema Loading**: We load a set of database schemas from JSON files, where each schema defines collections with their properties and data types.

2. **Operator Combinations**: We generate all valid combinations of query operators:
   - Search options (semantic search or none)
   - Filter options (integer, text, boolean filters, or none) 
   - Aggregation options (integer, text, boolean aggregations, or none)
   - Grouping options (groupby or none)

3. **Dynamic Model Creation**: For each operator combination, we:
   - Create a Pydantic model specifying required fields
   - Include descriptions of how each operator should be used
   - Require a natural language query that necessitates all selected operators

4. **LLM Query Generation**: Using GPT-4, we:
   - Provide the database schema and operator requirements
   - Generate natural language queries that require using all specified operators
   - Validate that queries can't be answered without using every selected operator

5. **Result Storage**: The generated queries are saved with:
   - The full database schema context
   - Structured Weaviate query parameters
   - Corresponding natural language questions
   - Metadata about which operators are used

This process generates 64 queries per schema, systematically covering different operator combinations while ensuring each query has a clear semantic purpose.

## Future

Several opportunities exist to enhance this synthetic query generation:

1. **Data-Grounded Queries**: Currently, queries are generated without actual collection data. Adding sample data would allow:
   - More realistic filter values and thresholds
   - Queries that reference existing data patterns
   - Validation that generated queries return meaningful results

2. **Business Context**: Each query could include:
   - Specific business scenarios requiring the query
   - User personas and their analytical needs
   - Justification for chosen parameter values
   - Alternative approaches that wouldn't suffice

3. **Query Complexity Scaling**:
   - Generate queries with multiple filters/aggregations
   - Include nested boolean logic in filters
   - Add multi-collection joins and relationships
   - Incorporate more complex grouping patterns

4. **Edge Cases and Error Handling**:
   - Generate queries that test boundary conditions
   - Include invalid operator combinations
   - Test error message clarity
   - Validate schema constraint handling

5. **Template-Based Generation**:
   - Create query templates for common patterns
   - Allow parameterized value insertion
   - Support domain-specific query types
   - Enable faster generation of similar queries

6. **Cross-Schema Relationships**:
   - Generate queries spanning multiple schemas
   - Test schema migration scenarios
   - Evaluate schema inference capabilities
   - Assess schema evolution handling