from pydantic import BaseModel
from typing import Any
from lm import LMService
from vectorizer import VectorizerService

def CreateObjects(
        num_samples: int,
        task_instructions: str, 
        output_model: BaseModel,
        lm_service: LMService,
        vectorizer_service: VectorizerService,
        reference_objects: dict[str, list[dict]] = None
    ) -> list[dict]:
    print("\033[92mCreating Objects:\033[0m")
    objects = []
    
    if reference_objects:
        combinations = _generate_combinations(reference_objects)
        for combination in combinations:
            formatted_instructions = format_task_instructions_with_reference(task_instructions, combination)
            response = LMService.generate(
                formatted_instructions,
                output_model
            )
            objects.append(response.model_dump_json())
            
            if len(objects) % 10 == 9:
                # deduplicate
                objects = _vector_deduplicator(
                    objects,
                    # Add necessary parameters here
                )
    else:
        for samples_generated_counter in range(num_samples):
            response = lm_service.generate(
                task_instructions,
                output_model
            )
            print(f"\033[92mResponse {samples_generated_counter}\033[0m")
            print(f"\033[1m{response.model_dump_json()}\033[0m\n")
            objects.append(response.model_dump_json())
    
    return objects

def _generate_combinations(reference_objects: dict[str, list[dict]]) -> list[dict]:
    from itertools import product
    
    keys = list(reference_objects.keys())
    values = [reference_objects[key] for key in keys]
    
    combinations = []
    for combo in product(*values):
        combination = {keys[i]: combo[i] for i in range(len(keys))}
        combinations.append(combination)
    
    return combinations

def format_task_instructions_with_reference(task_instructions: str, reference_objects: dict) -> str:
    return f"""
    task_instructions: {task_instructions}
    reference_objects: {reference_objects}
    """

# Need a dedup `key` in the case of the objects having multiple properties
def _vector_deduplicator(
        objects: list[dict], 
        vectorizer: VectorizerService, 
        dedup_threshold: int
    ) -> list[Any]:
    objects_copy = objects.copy()
    vectors = []
    for idx, obj in enumerate(objects):
        vectors.append({
            "idx": idx,
            "vector": vectorizer.vectorize(obj)
        })
    # ToDo, optionally mark vectors are duplicates based on vector distance OR..
    # OR.. (continued)
    # 1. reduce the dimensionality of vectors using t-SNE
    # 2. cluster the vectors using HDBSCAN
    # 3. inspect the clusters for duplicates (rather than comparing all objects)
    
    # Thinking the clustering approach will scale better when generating a massive number of objects

    for vector in vectors:
        for comparative_vector in vectors:
            pass
            # compute distance
            # if distance < threshold t (say 0.05)
            # mark as duplicate
    # remove duplicates
    
    # if deduplication_strategy = "vector_distance":
    #   Resolve duplicates by keeping the vector with the earliest index.
    #   For example if object 2 is 0.03 distance to object 8,
    #   => Remove object 8, because 2 < 8

    # if deduplication_strategy = "llm_resolver":
    #   Resolve duplicates by sending a prompt to the LLM to output the ids of objects that should be removed

    return objects_copy
