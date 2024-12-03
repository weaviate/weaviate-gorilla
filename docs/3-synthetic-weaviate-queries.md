# Synthetic Weaviate Queries

## Introduction

To evaluate the ability of large language models (LLMs) to translate natural language queries into search database API calls, we present a comprehensive test dataset that covers a diverse combinations of query APIs. These capabilities include search queries for finding relevant results based on scoring algorithms, property filters for matching on integer, text, and boolean fields, aggregations for computing statistics over integer, text, and boolean properties, and grouping operations to segment results by property values. Similarly to the Gorilla LLM, we use the Self-Instruct technique to generate synthetic queries that exercise these capabilities across different database schemas.

## Methodology

The query generation process follows a systematic approach to create comprehensive test cases. We begin by loading database schemas from JSON files that define collections with their properties and data types. Next, we generate all valid combinations of query operators, including options for semantic search, filters (integer, text, boolean), aggregations, and grouping operations. For each operator combination, we create a Pydantic model that specifies required fields and includes descriptions of how each operator should be used, ensuring that the natural language query necessitates all selected operators.

Using GPT-4, we then generate natural language queries by providing the database schema and operator requirements, validating that each query requires all specified operators to be answered correctly. The generated queries are stored along with their full database schema context, structured Weaviate query parameters, corresponding natural language questions, and metadata about which operators are used. This process yields 64 queries per schema, methodically covering different operator combinations while maintaining clear semantic purpose for each query.

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