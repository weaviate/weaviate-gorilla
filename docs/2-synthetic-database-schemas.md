# Synthetic Database Schemas

## Introduction

To evaluate LLMs' ability to interface with search-enabled databases, we developed a suite of synthetic database schemas. Each schema represents a distinct business domain and consists of three interrelated collections. Every collection is carefully designed with a searchable text property and three additional properties, one numeric, one textual, and one boolean, to enable comprehensive testing of different query patterns. This structured approach allows us to systematically assess how well LLMs can interpret database schemas and translate natural language requests into appropriate database operations.

## Methodology

The schema generation process leverages GPT-4 to create synthetic database schemas through a structured prompt engineering approach implemented in generate-schemas.py. The script takes a reference example schema that demonstrates the desired structure and detail level, along with specific requirements for each collection including two TEXT properties (one identifier and one rich searchable content), one NUMBER property for metrics/quantities, and one BOOLEAN property for flags/statuses. The generator ensures collections are meaningfully related and support business operations. Using these inputs, it produces 5 schema sets, each containing 3 interconnected collections - for instance, one schema set models a restaurant system with Restaurants, Menus, and Reservations collections, where Restaurants includes searchable descriptions of cuisine and ambiance, while Menus contains detailed item descriptions supporting dietary preference filtering. Each generated schema follows consistent conventions with collection names in camelCase format, comprehensive property definitions including types and detailed descriptions, use case overviews explaining collection relationships, and semantic search capabilities enabled through rich text fields.

## Future

The synthetic schema generation process could be enhanced in several ways:

1. Expanding property type variety to include dates, arrays, and nested objects
2. Generating sample data that aligns with schema constraints
3. Adding more complex relationships between collections
4. Incorporating industry-specific patterns and best practices
5. Generating accompanying test queries that exercise different query patterns

These improvements would create more comprehensive test cases for evaluating LLM query generation capabilities across a broader range of real-world scenarios.