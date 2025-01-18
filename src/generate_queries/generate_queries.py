import json
import itertools
import time
from typing import Optional, List, Dict
from pydantic import BaseModel, create_model, Field
from src.lm.lm import LMService
from src.vectorizer.vectorizer import VectorizerService
from src.models import (
    WeaviateQuery,
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation
)
import os
import tiktoken

print("Starting query generation script...")

# Initialize tokenizer
encoding = tiktoken.encoding_for_model("gpt-4")

# Initialize token counters
total_input_tokens = 0
total_output_tokens = 0
num_requests = 0

# Initialize query tracking
total_queries_generated = 0
total_queries_verified = 0
total_queries_valid = 0
start_time = time.time()

# -----------------------------
# Operator descriptions
# -----------------------------
print("Loading operator descriptions...")
search_query_desc = """Use `search_query` when you need to find the most relevant results..."""

text_property_filter_desc = """Use `text_property_filter` when you need to retrieve objects..."""

int_property_filter_desc = """Use `int_property_filter` when you need to return objects..."""

boolean_property_filter_desc = """Use `boolean_property_filter` when you need to retrieve objects..."""

text_property_aggregation_desc = """Use `text_property_aggregation` when you need to compute aggregate values..."""

int_property_aggregation_desc = """Use `int_property_aggregation` when you need to perform aggregate calculations..."""

boolean_property_aggregation_desc = """Use `boolean_property_aggregation` when you need to aggregate data..."""

groupby_desc = """Use `groupby` when you need to organize or segment results..."""

# -----------------------------
# LLM + Vectorizer initialization
# -----------------------------
def init_services(api_key: str) -> tuple[LMService, VectorizerService]:
    """
    Initialize LM and Vectorizer services.
    """
    print("Initializing LM and Vectorizer services...")
    lm_service = LMService(
        model_provider="openai",
        model_name="gpt-4o",        # or your chosen GPT-4 model alias
        api_key=api_key
    )
    
    vectorizer_service = VectorizerService(
        model_provider="openai",
        model_name="text-embedding-3-small",
        api_key=api_key
    )
    print("Services initialized successfully")
    
    return lm_service, vectorizer_service

# -----------------------------
# Utility for printing schema
# -----------------------------
def format_schema(schema: Dict) -> str:
    """
    Format schema as pretty-printed JSON string.
    """
    print("Formatting database schema...")
    return json.dumps(schema, indent=2)

# -----------------------------
# Prompt for query generation
# -----------------------------
def get_query_prompt() -> str:
    """
    Get the base query generation prompt.
    """
    print("Building query generation prompt...")
    return """
You are generating natural language database queries that MUST use specific Weaviate query operators.

[[ Available Operators ]]
{operator_description}

[[ Database Schema ]]
{database_schema}

Instructions:
1. Your natural language query MUST use ALL operators listed above, and ONLY those operators
2. You MUST explicitly mention the exact property names from the schema that each operator will use
3. You MUST make the numeric values, comparison operators, and property names clear in your query

Examples:

GOOD QUERY (for integer_property_filter on 'appointmentDuration'):
"Find appointments that are at least 30 minutes in appointmentDuration"
- Explicitly references the property name
- Makes the comparison clear
- Value is unambiguous

BAD QUERY (for integer_property_filter on 'appointmentDuration'):
"Find appointments for young patients with experienced doctors"
- Doesn't reference the actual property
- Unclear what properties or values to filter on
- Could be interpreted multiple ways

Remember:
- Be explicit about property names
- Include clear numeric values when using filters
- Make it obvious which operator applies to which part of the query
- Don't introduce requirements that would need additional operators (THIS IS VERY IMPORTANT!!)

Generate a single natural language query meeting these requirements."""

# -----------------------------
# Verification Model + Prompt
# -----------------------------
class QueryVerificationModel(BaseModel):
    """
    A model for the second inference step, which checks the correctness of a query.
    """
    is_valid: bool = Field(
        ...,
        description="True if the generated query aligns with the ground-truth operators or appears correct; False otherwise"
    )

def get_verification_prompt(
    generated_query: dict,
    ground_truth_operators: List[str],
    execution_result: str = None
) -> str:
    """
    Build the prompt for verifying a generated query.
    """
    print("Building verification prompt...")
    instructions = """
You are checking the correctness of an AI-generated query that corresponds to specific database operators.

- If the query actually uses the expected operators in a sensible way and the result is consistent, answer True.
- If the query is missing operators, uses different operators, or the result is suspiciously incorrect, answer False.

Important: Provide the final JSON with a single boolean field "is_valid".
"""

    if execution_result:
        instructions += f"\nExecution result:\n{execution_result}\n"
    instructions += f"\nGround truth operators: {ground_truth_operators}\n"
    instructions += f"Generated query:\n{generated_query}\n"
    instructions += "\nOnly output JSON with the single key 'is_valid', e.g. `{\"is_valid\": true}`."
    return instructions

def verify_query(
    lm_service: LMService,
    generated_query: dict,
    ground_truth_operators: List[str],
    execution_result: str = None
) -> bool:
    """
    Performs a second inference step to verify if the generated query is consistent
    with the ground truth operators and possibly the execution result.
    Returns True if consistent/correct, False otherwise.
    """
    global total_input_tokens, total_output_tokens, num_requests, total_queries_verified, total_queries_valid
    
    print(f"Verifying query with ground truth operators: {ground_truth_operators}")
    prompt = get_verification_prompt(
        generated_query=generated_query,
        ground_truth_operators=ground_truth_operators,
        execution_result=execution_result
    )
    
    # Count input tokens
    input_tokens = len(encoding.encode(prompt))
    total_input_tokens += input_tokens
    
    # Ask the model to produce JSON matching QueryVerificationModel
    verification_output = lm_service.generate(prompt, QueryVerificationModel)
    
    # Count output tokens
    output_tokens = len(encoding.encode(str(verification_output.model_dump())))
    total_output_tokens += output_tokens
    num_requests += 1
    
    # Update verification stats
    total_queries_verified += 1
    if verification_output.is_valid:
        total_queries_valid += 1
    
    # Calculate and display verification statistics
    verification_rate = (total_queries_valid / total_queries_verified) * 100
    print(f"\033[32mQuery verification result: {verification_output.is_valid}\033[0m")
    print(f"\033[36mVerification Statistics:")
    print(f"Total queries verified: {total_queries_verified}")
    print(f"Total queries valid: {total_queries_valid}")
    print(f"Verification success rate: {verification_rate:.1f}%\033[0m")
    print(f"Tokens used - Input: {input_tokens}, Output: {output_tokens}")
    return verification_output.is_valid

# -----------------------------
# Query Generation
# -----------------------------
def generate_single_query(
    schema: Dict,
    search: Optional[tuple] = None,
    filter_: Optional[tuple] = None,
    agg: Optional[tuple] = None,
    group: Optional[tuple] = None,
    lm_service: Optional[LMService] = None
) -> Dict:
    """
    Generate a single query with the specified combination of operators.
    """
    global total_input_tokens, total_output_tokens, num_requests, total_queries_generated
    
    print("\nGenerating single query...")
    print(f"Operators: Search={search}, Filter={filter_}, Aggregation={agg}, Group={group}")
    
    # Build properties dict for dynamic model
    properties = {
        "target_collection": (
            str, 
            Field(..., description="The name of the Weaviate collection to query")
        ),
        "reflection_of_APIs_that_will_be_used_in_this_query": (
            str, 
            Field(..., description="A description of which Weaviate APIs will be needed to execute this query")
        ),
    }
    
    # Build operator description for prompt
    operator_desc = []
    
    if search:
        properties[search[0]] = (search[1], ...)
        operator_desc.append(search_query_desc)
        
    if filter_:
        properties[filter_[0]] = (filter_[1], ...)
        if filter_[0] == "integer_property_filter":
            operator_desc.append(int_property_filter_desc)
        elif filter_[0] == "text_property_filter":
            operator_desc.append(text_property_filter_desc)
        else:
            operator_desc.append(boolean_property_filter_desc)
            
    if agg:
        properties[agg[0]] = (agg[1], ...)
        if agg[0] == "integer_property_aggregation":
            operator_desc.append(int_property_aggregation_desc)
        elif agg[0] == "text_property_aggregation":
            operator_desc.append(text_property_aggregation_desc)
        else:
            operator_desc.append(boolean_property_aggregation_desc)
            
    if group:
        properties[group[0]] = (group[1], ...)
        operator_desc.append(groupby_desc)

    properties["corresponding_natural_language_query"] = (
        str, 
        Field(..., description="The natural language question that this query is designed to answer.")
    )

    print("Creating dynamic query model...")
    # Create dynamic model
    DynamicQueryModel = create_model(
        'DynamicQueryModel', 
        **properties
    )
    
    print("Generating query using language model...")
    # Generate query using LM
    task_instructions = get_query_prompt().format(
        operator_description="\n".join(operator_desc),
        database_schema=format_schema(schema)
    )
    
    # Count input tokens
    input_tokens = len(encoding.encode(task_instructions))
    total_input_tokens += input_tokens
    
    query = lm_service.generate(task_instructions, DynamicQueryModel)
    
    # Count output tokens
    output_tokens = len(encoding.encode(str(query.model_dump())))
    total_output_tokens += output_tokens
    num_requests += 1
    
    query_dict = query.model_dump()
    
    print("Converting to WeaviateQuery format...")
    # Convert to WeaviateQuery
    weaviate_query = WeaviateQuery(
        corresponding_natural_language_query=query_dict["corresponding_natural_language_query"],
        target_collection=query_dict["target_collection"],
        search_query=query_dict.get("search_query"),
        integer_property_filter=query_dict.get("integer_property_filter"),
        text_property_filter=query_dict.get("text_property_filter"),
        boolean_property_filter=query_dict.get("boolean_property_filter"),
        integer_property_aggregation=query_dict.get("integer_property_aggregation"),
        text_property_aggregation=query_dict.get("text_property_aggregation"),
        boolean_property_aggregation=query_dict.get("boolean_property_aggregation"),
        groupby_property=query_dict.get("groupby_property")
    )
    
    total_queries_generated += 1
    elapsed_time = time.time() - start_time
    avg_time_per_query = elapsed_time / total_queries_generated
    
    print("Query generation complete")
    print(f"\033[32mGenerated natural language query: {query_dict['corresponding_natural_language_query']}\033[0m")
    print(f"\033[36mProgress: Generated {total_queries_generated} queries so far")
    print(f"Average time per query: {avg_time_per_query:.1f} seconds\033[0m")
    print(f"Tokens used - Input: {input_tokens}, Output: {output_tokens}")
    return weaviate_query.model_dump()

# -----------------------------
# Helper: Identify the Operators We Used
# -----------------------------
def get_ground_truth_operators(
    search: Optional[tuple],
    filter_: Optional[tuple],
    agg: Optional[tuple],
    group: Optional[tuple]
) -> List[str]:
    """
    Return a list of operator names that we expect based on the (search, filter, agg, group)
    arguments. E.g. ["search_query", "integer_property_filter"] etc.
    """
    print("Getting ground truth operators...")
    ops = []
    if search:
        ops.append(search[0])
    if filter_:
        ops.append(filter_[0])
    if agg:
        ops.append(agg[0])
    if group:
        ops.append(group[0])
    print(f"Ground truth operators: {ops}")
    return ops

# -----------------------------
# Generate all queries
# -----------------------------
def generate_all_queries(schemas: List[Dict], api_key: str) -> List[Dict]:
    """
    Generate all possible query combinations for the given schemas
    and verify correctness with a second inference step.
    """
    print("\nStarting generation of all possible queries...")
    lm_service, _ = init_services(api_key)
    
    print("Setting up operator combinations...")
    # Possible operator combos
    search_options = [("search_query", str), None]
    filter_options = [
        ("integer_property_filter", IntPropertyFilter),
        ("text_property_filter", TextPropertyFilter),
        ("boolean_property_filter", BooleanPropertyFilter),
        None
    ]
    aggregation_options = [
        ("integer_property_aggregation", IntAggregation),
        ("text_property_aggregation", TextAggregation),
        ("boolean_property_aggregation", BooleanAggregation),
        None
    ]
    groupby_options = [("groupby_property", str), None]
    
    results = []
    
    # Calculate total number of combinations
    total_combinations = len(schemas) * (
        len(search_options) * len(filter_options) * 
        len(aggregation_options) * len(groupby_options) - 1  # Subtract 1 for all-None case
    )
    print(f"\033[36mExpecting to generate approximately {total_combinations} queries in total\033[0m")
    
    # Cartesian product of all operator combos
    print(f"Processing {len(schemas)} schemas...")
    for schema_idx, schema in enumerate(schemas, 1):
        print(f"\nProcessing schema {schema_idx}/{len(schemas)}")
        combinations_processed = 0
        
        for search, filter_, agg, group in itertools.product(
            search_options,
            filter_options,
            aggregation_options,
            groupby_options
        ):
            # Skip case where all four are None (i.e. no operators at all)
            if not any([search, filter_, agg, group]):
                print("Skipping combination with no operators")
                continue
            
            combinations_processed += 1
            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / total_queries_generated) * total_combinations if total_queries_generated > 0 else 0
            estimated_remaining_time = max(0, estimated_total_time - elapsed_time)
            
            print(f"\033[36mProgress: Schema {schema_idx}/{len(schemas)}, Combination {combinations_processed}")
            print(f"Estimated time remaining: {estimated_remaining_time/60:.1f} minutes\033[0m")
            
            print("\nGenerating query with operators:")
            print(f"Search: {search}")
            print(f"Filter: {filter_}")
            print(f"Aggregation: {agg}")
            print(f"Group: {group}")
            
            # 1) Generate the query
            query = generate_single_query(
                schema=schema,
                search=search,
                filter_=filter_,
                agg=agg,
                group=group,
                lm_service=lm_service
            )
            
            # 2) Build a "ground truth" list of operators we expect
            ground_truth_ops = get_ground_truth_operators(search, filter_, agg, group)
            
            # 3) (Optional) If you have an actual execution result, pass it here
            # For this example, we'll pass None
            execution_result = None
            
            # 4) Verify the query with a second LLM call
            is_valid = verify_query(
                lm_service=lm_service,
                generated_query=query,
                ground_truth_operators=ground_truth_ops,
                execution_result=execution_result
            )
            
            results.append({
                "database_schema": schema,
                "query": query,
                "ground_truth_operators": ground_truth_ops,
                "is_valid": is_valid
            })
            
    print(f"\nQuery generation complete. Generated {len(results)} queries.")
    
    # Print token usage statistics
    print("\nToken Usage Statistics:")
    print(f"Total input tokens: {total_input_tokens}")
    print(f"Total output tokens: {total_output_tokens}")
    print(f"Average input tokens per request: {total_input_tokens/num_requests:.1f}")
    print(f"Average output tokens per request: {total_output_tokens/num_requests:.1f}")
    
    return results

# -----------------------------
# Main script entry point
# -----------------------------
if __name__ == "__main__":
    print("Starting main script execution...")
    
    # Load schemas from a JSON file (adjust path as needed)
    print("Loading database schemas...")
    with open("../../data/3-collection-schemas-with-search-property.json", "r") as json_file:
        database_schemas = json.load(json_file)
    print(f"Loaded {len(database_schemas)} schemas")
    
    # Read your API key from environment or otherwise
    print("Getting API key...")
    api_key = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")
    
    # Generate and verify queries
    print("Starting query generation process...")
    results = generate_all_queries(database_schemas, api_key)
    
    # Save results to a JSON file
    print("Saving results to file...")
    with open("synthetic-weaviate-queries-with-schemas.json", "w") as file:
        json.dump(results, file, indent=4)

    print("Done! Generated queries have been saved.")
