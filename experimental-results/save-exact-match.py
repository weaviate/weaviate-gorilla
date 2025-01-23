import json
import os
import glob

# Get all JSON files in results directory
result_files = glob.glob('results/*.json')

for file_path in result_files:
    # Read the JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Count exact matches (AST score of 1.0)
    exact_matches = 0
    total_queries = data["total_queries"]  # Use total queries from data
    
    # Loop through all queries
    for query in data["detailed_results"]:
        # Only count if there's a perfect AST score
        if query.get('ast_score') == 1.0:
            exact_matches += 1
    
    # Calculate percentage out of total queries
    exact_match_pct = (exact_matches / total_queries) * 100
        
    # Add exact match percentage to data
    data['exact_match_pct'] = exact_match_pct
    
    # Write updated data back to file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
        
print("Exact match percentages calculated and saved")
