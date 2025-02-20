import json

INPUT_FILE = "./synthetic-weaviate-queries-with-schemas.json"
OUTPUT_FILE = "./updated-queries-with-schemas.json"

def update_query(query: dict) -> dict:
    """
    Update the aggregations in the query:
    - Map COUNT to total_count=True (and remove that aggregation)
    - Remove any aggregation with metric TYPE
    """
    # List of aggregation fields to check
    agg_fields = [
        "integer_property_aggregation",
        "text_property_aggregation",
        "boolean_property_aggregation"
    ]
    
    for field in agg_fields:
        agg = query.get(field)
        if agg is not None:
            metric = agg.get("metrics")
            if metric == "COUNT":
                # Remove the aggregation and set total_count
                query[field] = None
                query["total_count"] = True
            elif metric == "TYPE":
                # Remove the aggregation entirely
                query[field] = None
    return query

def main():
    # Load the original file
    with open(INPUT_FILE, "r") as infile:
        data = json.load(infile)
    
    # Process each record if it contains a query
    for record in data:
        if "query" in record and isinstance(record["query"], dict):
            record["query"] = update_query(record["query"])
    
    # Write out the updated data to a new file
    with open(OUTPUT_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)
    
    print(f"Updated queries written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
