import json
import os
import glob

# Get all JSON files in results directory
result_files = glob.glob('results/*.json')

for file_path in result_files:
    # Read the JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Count correct collection routing
    correct_collections = 0
    total_queries = data['total_queries']  # Get total queries from metadata
    
    # Loop through all queries
    for query in data["detailed_results"]:
        # Skip if error or no predicted query
        if query.get('error') is not None or query.get('predicted_query') is None:
            continue
            
        # Check collection routing
        ground_truth_collection = query['ground_truth_query']['target_collection']
        predicted_collection = query['predicted_query']['target_collection']
        if ground_truth_collection == predicted_collection:
            correct_collections += 1
    
    # Calculate percentage out of total queries
    collection_routing_accuracy = (correct_collections / total_queries) * 100
        
    # Add metric to data
    data['collection_routing_accuracy'] = collection_routing_accuracy
    
    # Write updated data back to file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
        
print("Collection routing accuracy percentage calculated and saved")
