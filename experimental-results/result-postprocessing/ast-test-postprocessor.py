# Calculate per API accuracy from AST scores

import json
from typing import Dict, List, Optional
from pydantic import BaseModel

# Load experiment results
with open("../gpt-4o-mini-experiment-results.json", "r") as f:
    results = json.load(f)

total_queries = results["total_queries"]
successful_predictions = results["successful_predictions"] 
failed_predictions = results["failed_predictions"]
average_ast_score = results["average_ast_score"]

# Print summary statistics
print(f"Total queries analyzed: {total_queries}")
print(f"Successful predictions: {successful_predictions}")
print(f"Failed predictions: {failed_predictions}")
print(f"Average AST score: {average_ast_score:.2%}")

# Print per schema scores
print("\nPer schema scores:")
for schema_id, score in results["per_schema_scores"].items():
    print(f"Schema {schema_id}: {score:.2%}")
