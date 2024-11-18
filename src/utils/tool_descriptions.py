# Collection name descriptions with slight variations to encourage diversity
collection_name_descriptions = [
    "The collection to query - select from available collections",
    "Choose which collection to query from the available options",
    "Specify which collection you want to query",
    "Select the target collection for this query",
    "Pick the collection you want to query from the list"
]

# Search query descriptions with variations
search_query_descriptions = [
    "Optional search query to find semantically relevant items.",
    "Optional semantic search query to find relevant records.",
    "Optional natural language search to find matching items.",
    "Optional search text to find semantically similar records.",
    "Optional query text to find relevant matches."
]

# Filter string descriptions with variations but maintaining key information
filter_string_descriptions = [
    """
    Optional filter expression using prefix notation to ensure unambiguous order of operations.
    
    Basic condition syntax: property_name:operator:value
    
    Compound expressions use prefix AND/OR with parentheses:
    - AND(condition1, condition2)
    - OR(condition1, condition2) 
    - AND(condition1, OR(condition2, condition3))
    
    Examples:
    - Simple: age:>:25
    - Compound: AND(age:>:25, price:<:1000)
    - Complex: OR(AND(age:>:25, price:<:1000), category:=:'electronics')
    - Nested: AND(status:=:'active', OR(price:<:50, AND(rating:>:4, stock:>:100)))
    
    Supported operators:
    - Comparison: =, >, <, >=, <= 
    - Text only: LIKE

    IMPORTANT!!! Please review the collection schema to make sure the property name is spelled correctly!! THIS IS VERY IMPORTANT!!!
    """,
    """
    Optional filter using prefix notation (property_name:operator:value).
    
    Use AND/OR with parentheses for compound filters:
    AND(condition1, condition2)
    OR(condition1, condition2)
    
    Examples:
    age:>:25
    AND(age:>:25, price:<:1000)
    
    Operators: =, >, <, >=, <=, LIKE(text only)
    
    IMPORTANT: Property names must match schema exactly!
    """,
    """
    Optional property filter with syntax: property_name:operator:value
    
    Combine with AND/OR: AND(filter1, filter2)
    
    Example: AND(price:<:50, rating:>:4)
    
    Valid operators: =, >, <, >=, <=, LIKE(text)
    
    NOTE: Property names must match schema!
    """,
    """
    Optional filtering with property_name:operator:value
    
    Combine multiple: AND(...) or OR(...)
    
    Example: OR(price:<:20, rating:>=:4.5)
    
    Use: =, >, <, >=, <=, LIKE(text only)
    
    CRITICAL: Use exact property names from schema
    """,
    """
    Optional filters on properties (property:operator:value)
    
    Join with AND/OR in prefix notation
    
    Example: AND(inStock:=:true, price:<:100)
    
    Operators: =, >, <, >=, <=, LIKE(text)
    
    WARNING: Property names must match schema!
    """
]

# Aggregation string descriptions with variations
aggregation_string_descriptions = [
    """
    Optional aggregate expression using syntax: property_name:aggregation_type.

    Group by with: GROUP_BY(property_name) (limited to one property).

    Aggregation Types by Data Type:

    Text: COUNT, TYPE, TOP_OCCURRENCES[limit]
    Numeric: COUNT, TYPE, MIN, MAX, MEAN, MEDIAN, MODE, SUM
    Boolean: COUNT, TYPE, TOTAL_TRUE, TOTAL_FALSE, PERCENTAGE_TRUE, PERCENTAGE_FALSE
    Date: COUNT, TYPE, MIN, MAX, MEAN, MEDIAN, MODE

    Examples:
    Simple: Article:COUNT, wordCount:COUNT,MEAN,MAX, category:TOP_OCCURRENCES[5]
    Grouped: GROUP_BY(publication):COUNT, GROUP_BY(category):COUNT,price:MEAN,MAX

    Combine with commas: GROUP_BY(publication):COUNT,wordCount:MEAN,category:TOP_OCCURRENCES[5]
    """,
    """
    Optional aggregations: property:aggregation_type
    
    Group with GROUP_BY(property)
    
    Available aggregations:
    - Text: COUNT, TYPE, TOP_OCCURRENCES[n]
    - Numbers: COUNT, TYPE, MIN, MAX, MEAN, MEDIAN, MODE, SUM
    - Boolean: COUNT, TYPE, TOTAL_TRUE/FALSE, PERCENTAGE_TRUE/FALSE
    - Dates: COUNT, TYPE, MIN, MAX, MEAN, MEDIAN, MODE
    
    Example: GROUP_BY(category):COUNT,price:MEAN
    """,
    """
    Optional property aggregations (property:aggregation)
    
    Use GROUP_BY(property) for grouping
    
    Aggregations per type:
    Text: COUNT, TYPE, TOP_OCCURRENCES[n]
    Numeric: COUNT, TYPE, MIN, MAX, MEAN, MEDIAN, MODE, SUM
    Boolean/Date: Various statistics
    
    Example: sales:SUM,category:TOP_OCCURRENCES[3]
    """,
    """
    Optional aggregate functions on properties
    
    GROUP_BY(property) for grouping
    
    Functions:
    - Text: COUNT, TYPE, TOP_OCCURRENCES[n]
    - Numbers: Statistics (MIN,MAX,MEAN,etc)
    - Boolean/Date: Type-specific stats
    
    Example: GROUP_BY(region):COUNT,revenue:SUM
    """,
    """
    Optional property aggregations
    
    Group using GROUP_BY(property)
    
    Available:
    - Text: Basic stats + TOP_OCCURRENCES
    - Numeric: Full statistics
    - Boolean/Date: Type-specific metrics
    
    Example: GROUP_BY(type):COUNT,rating:MEAN
    """
]
