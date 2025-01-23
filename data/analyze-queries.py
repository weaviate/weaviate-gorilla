import json
from collections import Counter, defaultdict
from typing import Dict, List, Set
import itertools

def analyze_operator_distribution(data: List[Dict]) -> None:
    """
    Analyze the distribution of operators in the generated queries.
    """
    # Initialize counters
    total_queries = len(data)
    valid_queries = sum(1 for item in data if item['is_valid'])
    operator_counts = Counter()
    operator_combinations = Counter()
    schemas_covered = set()
    
    # Count operator occurrences and combinations
    for item in data:
        # Track schemas
        schema_str = json.dumps(item['database_schema'], sort_keys=True)
        schemas_covered.add(schema_str)
        
        # Get operators used in this query
        operators = set(item['ground_truth_operators'])
        
        # Count individual operators
        for op in operators:
            operator_counts[op] += 1
            
        # Count operator combinations
        operator_combinations[tuple(sorted(operators))] += 1
    
    # Print results
    print("\n=== Query Generation Analysis ===")
    print(f"\nTotal Queries: {total_queries}")
    print(f"Valid Queries: {valid_queries} ({(valid_queries/total_queries)*100:.1f}%)")
    print(f"Unique Schemas Used: {len(schemas_covered)}")
    
    print("\n=== Individual Operator Distribution ===")
    for operator, count in sorted(operator_counts.items()):
        percentage = (count / total_queries) * 100
        print(f"{operator}: {count} ({percentage:.1f}%)")
    
    print("\n=== Operator Combination Distribution ===")
    for combo, count in sorted(operator_combinations.items(), key=lambda x: (-len(x[0]), x[0])):
        percentage = (count / total_queries) * 100
        print(f"{' + '.join(combo)}: {count} ({percentage:.1f}%)")
    
    # Verify completeness of combinations
    print("\n=== Completeness Analysis ===")
    operator_types = {
        'search': ['search_query'],
        'filter': ['integer_property_filter', 'text_property_filter', 'boolean_property_filter'],
        'aggregation': ['integer_property_aggregation', 'text_property_aggregation', 'boolean_property_aggregation'],
        'group': ['groupby_property']
    }
    
    # Generate all possible valid combinations
    all_possible_combinations = set()
    for r in range(1, len(operator_types) + 1):
        for type_combo in itertools.combinations(operator_types.keys(), r):
            # Get all possible operator combinations for these types
            type_operators = [operator_types[t] for t in type_combo]
            for op_combo in itertools.product(*type_operators):
                all_possible_combinations.add(tuple(sorted(op_combo)))
    
    # Check which combinations are missing
    actual_combinations = set(operator_combinations.keys())
    missing_combinations = all_possible_combinations - actual_combinations
    
    print(f"\nFound {len(actual_combinations)} unique operator combinations")
    print(f"Expected {len(all_possible_combinations)} possible combinations")
    
    if missing_combinations:
        print("\nMissing combinations:")
        for combo in sorted(missing_combinations, key=lambda x: (len(x), x)):
            print(f"- {' + '.join(combo)}")
    else:
        print("\nAll possible operator combinations are present!")

def main():
    # Load the generated queries
    try:
        with open('synthetic-weaviate-queries-with-results.json', 'r') as f:
            data = json.load(f)
        analyze_operator_distribution(data)
    except FileNotFoundError:
        print("Error: Could not find the queries file. Make sure it's in the current directory.")
    except json.JSONDecodeError:
        print("Error: Could not parse the JSON file. Make sure it's properly formatted.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()