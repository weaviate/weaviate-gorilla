zero_shot_baseline = ""

weaviate_query_api_docs = """
The Database Query Tool provides a flexible interface for querying collections within a database. It supports various operations including full-text search, filtering, aggregations, and grouping. This tool is designed to handle different data types (integer, text, and boolean) with type-specific operations.

Basic Usage
At minimum, each query must specify a collection_name. All other parameters are optional and can be combined to create complex queries.

Core Parameters and Search:
The required parameter is collection_name, which specifies which collection to query. The search_query parameter is ESSENTIAL for finding items based on descriptive terms or phrases - you must use it whenever searching for descriptive qualities of items. Never use text filters (LIKE) for descriptive searches. The groupby_property parameter allows grouping results by a specified property.

CRITICAL: Search vs. Filters
1. ALWAYS use search_query for:
   - Any descriptive terms ("romantic", "cozy", "relaxing")
   - Atmosphere descriptions ("romantic atmosphere", "cozy ambiance")
   - Restaurant types ("brunch spots", "dining locations")
   - Amenities ("outdoor seating")
   - Special characteristics ("vegan-friendly")
   - Combinations of these ("romantic Italian restaurants", "cozy dining spots")

2. NEVER use text filters (LIKE operator) for:
   - Descriptive terms
   - Atmosphere
   - Restaurant types
   - Amenities
   - Special characteristics

3. Use filters ONLY for:
   - Exact numeric comparisons (rating > 4)
   - Exact property matching
   - Boolean conditions

Correct Examples:
✓ search_query: "romantic Italian restaurants"
✓ search_query: "vegan-friendly brunch spots"
✓ search_query: "romantic dining locations"
✓ search_query: "restaurants with relaxing atmosphere"

Incorrect Examples:
✗ text_filter: description LIKE "romantic"
✗ text_filter: description LIKE "vegan"
✗ text_filter: description LIKE "relaxing"
✗ boolean_filter: openNow = True (when calculating percentages)

Key Points About Aggregations:
1. When asked about "how many", use COUNT aggregation
2. When asked about percentages of boolean properties, use PERCENTAGE_TRUE aggregation
3. When asked about "most common" or "typical" text features, use TOP_OCCURRENCES
4. When asked about averages, always include the appropriate MEAN aggregation

Property Usage Rules:
1. For cuisine grouping, use "description.cuisine" as the property
2. For open/closed status:
   - Use boolean_aggregation with PERCENTAGE_TRUE when calculating percentages
   - Use groupby: "openNow" when grouping results
   - Don't use boolean filters unless specifically filtering, not aggregating

Aggregation Operations
The tool provides sophisticated aggregation capabilities for different data types:
Integer Aggregations: Use integer_property_aggregation for numeric analysis. Available metrics: COUNT, TYPE, MIN, MAX, MEAN, MEDIAN, MODE, SUM
Text Aggregations: Use text_property_aggregation for text analysis. Available metrics: COUNT, TYPE, TOP_OCCURRENCES
Boolean Aggregations: Use boolean_property_aggregation for boolean statistics. Available metrics: COUNT, TYPE, TOTAL_TRUE, TOTAL_FALSE, PERCENTAGE_TRUE, PERCENTAGE_FALSE
"""