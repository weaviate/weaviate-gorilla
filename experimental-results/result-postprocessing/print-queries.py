import json

with open("../claude-3-5-sonnet-experiment-results-with-models.json", "r") as f:
    results = json.load(f)

text_agg_queries = []
int_agg_queries = []
bool_agg_queries = []
no_agg_queries = []

for idx, result in enumerate(results["detailed_results"]):
    if idx > 63:
        break
    
    ground_truth = result["ground_truth_query"]
    nl_query = result["natural_language_query"]
    if ground_truth["text_property_aggregation"] is not None:
        text_agg_queries.append(nl_query)
    elif ground_truth["integer_property_aggregation"] is not None:
        int_agg_queries.append(nl_query)
    elif ground_truth["boolean_property_aggregation"] is not None:
        bool_agg_queries.append(nl_query)
    else:
        no_agg_queries.append(nl_query)

print("\nQueries with Text Property Aggregations:")
print("-" * 40)
for query in text_agg_queries:
    print(query)

print("\nQueries with Integer Property Aggregations:")
print("-" * 40)
for query in int_agg_queries:
    print(query)

print("\nQueries with Boolean Property Aggregations:")
print("-" * 40)
for query in bool_agg_queries:
    print(query)

print("\nQueries with No Aggregations:")
print("-" * 40)
for query in no_agg_queries:
    print(query)
