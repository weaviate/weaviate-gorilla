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
        reference_objects: dict[str, list[dict]] = None,
        dedup_strategy: str = "brute_force",
        dedup_params: dict = None
    ) -> list[dict]:
    """Creates a list of unique objects using a language model, with optional reference objects and deduplication.
    
    This function generates objects in two modes:
    1. With reference objects: Generates combinations of provided reference objects and creates new objects based on those
    2. Without reference objects: Generates the specified number of new objects from scratch
    
    In both modes, the function can apply various deduplication strategies to ensure uniqueness of generated objects.
    
    Args:
        num_samples (int): Number of objects to generate when not using reference objects
        task_instructions (str): Instructions for the language model on how to generate the objects
        output_model (BaseModel): Pydantic model defining the structure of generated objects
        lm_service (LMService): Service for interacting with the language model
        vectorizer_service (VectorizerService): Service for creating vector embeddings of objects
        reference_objects (dict[str, list[dict]], optional): Dictionary mapping reference object types to lists of objects.
            Used to generate combinations of reference objects. Defaults to None.
        dedup_strategy (str, optional): Strategy to use for deduplication. Options:
            - "brute_force": Checks each new object against all previous objects using LLM
            - "last_k": Checks each new object against the k most recent objects using LLM
            - "GRAD": Uses vector similarity + LLM verification
            - "clustering": Uses HDBSCAN clustering on vector embeddings
            Defaults to "brute_force".
        dedup_params (dict, optional): Parameters for the chosen deduplication strategy:
            - For "last_k": {"k": int} - number of recent objects to check against
            - For "GRAD": {"threshold": float} - similarity threshold for duplicate detection
            Defaults to None.
    
    Returns:
        list[dict]: List of generated objects as dictionaries, with duplicates removed according to the
            specified deduplication strategy.
    
    Prints:
        Progress messages showing:
        - Start of object creation
        - For non-reference mode: Each generated response and its index
    
    Deduplication Behavior:
        - "brute_force" and "last_k" are applied after each new object is generated
        - Other strategies are applied every 10 objects (when len(objects) % 10 == 9)
        - If no deduplication is desired, pass a strategy that doesn't match any known options
    """
    print("\033[92mCreating Objects:\033[0m")
    objects = []
    
    if reference_objects:
        # Not tested!
        combinations = _generate_combinations(reference_objects)
        for combination in combinations:
            formatted_instructions = format_task_instructions_with_reference(task_instructions, combination)
            response = LMService.generate(
                formatted_instructions,
                output_model
            )
            objects.append(response.model_dump_json())
            
            if dedup_strategy == "brute_force":
                objects = _deduplicate_brute_force(
                    objects=objects,
                    lm_service=lm_service,
                    task_instructions=task_instructions,
                    reference_objects=reference_objects,
                    output_model=output_model
                )
            elif dedup_strategy == "last_k":
                objects = _deduplicate_last_k(
                    objects=objects,
                    lm_service=lm_service,
                    task_instructions=task_instructions,
                    reference_objects=reference_objects,
                    output_model=output_model,
                    **dedup_params or {}
                )
            elif len(objects) % 10 == 9:
                objects = _deduplicate(
                    objects=objects,
                    strategy=dedup_strategy,
                    lm_service=lm_service,
                    vectorizer_service=vectorizer_service,
                    task_instructions=task_instructions,
                    reference_objects=reference_objects,
                    output_model=output_model,
                    **dedup_params or {}
                )
    else:
        # Only this has been tested!!
        # Generate first object
        response = lm_service.generate(
                task_instructions,
                output_model
            )
        print(f"\033[92mFirst response without deduplication.\033[0m")
        print(f"\033[1m{response.model_dump_json()}\033[0m\n")
        objects.append(response.model_dump_json())
        
        # Generate remaining objects with deduplication
        for samples_generated_counter in range(num_samples - 1):
            if dedup_strategy == "brute_force":
                # Get a new non-duplicate object
                response = _deduplicate_brute_force(
                    objects=objects,
                    lm_service=lm_service,
                    task_instructions=task_instructions,
                    reference_objects=reference_objects,
                    output_model=output_model
                )
                print(f"\033[92mResponse {samples_generated_counter + 1}\033[0m")
                print(f"\033[1m{response.model_dump_json()}\033[0m\n")
                objects.append(response.model_dump_json())

            elif dedup_strategy == "last_k":
                # Get a new non-duplicate object
                response = _deduplicate_last_k(
                    objects=objects,
                    lm_service=lm_service,
                    task_instructions=task_instructions,
                    reference_objects=reference_objects,
                    output_model=output_model,
                    **dedup_params or {}
                )
                print(f"\033[92mResponse {samples_generated_counter + 1}\033[0m")
                print(f"\033[1m{response.model_dump_json()}\033[0m\n")
                objects.append(response.model_dump_json())
            elif len(objects) % 10 == 9:
                # Batch deduplication every 10 objects
                objects = _deduplicate(
                    objects=objects,
                    strategy=dedup_strategy,
                    lm_service=lm_service,
                    vectorizer_service=vectorizer_service,
                    task_instructions=task_instructions,
                    reference_objects=reference_objects,
                    output_model=output_model,
                    **dedup_params or {}
                )
    
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

def format_brute_force_history_prompt(task_instructions: str, reference_objects: dict, objects: list[dict]) -> str:
    return f"""Given the following task and context:

    Original Task Instructions:
    {task_instructions}

    Reference Objects (if any):
    {reference_objects if reference_objects else 'None'}

    Previously Generated Samples:
    {objects}

    Please analyze these samples carefully and make sure not to generate a duplicate."""

def format_last_k_history_prompt(task_instructions: str, reference_objects: dict, recent_objects: list[dict], k: int, obj: dict) -> str:
    return f"""Given the following task and context:

    Original Task Instructions:
    {task_instructions}

    Reference Objects (if any):
    {reference_objects if reference_objects else 'None'}

    Recent {k} Samples:
    {recent_objects}

    New Sample to Check:
    {obj}

    Please analyze these samples carefully and make sure not to generate a duplicate."""

def _deduplicate_brute_force(
        objects: list[dict],
        lm_service: LMService,
        task_instructions: str,
        output_model: BaseModel,
        reference_objects: dict = None
    ) -> list[dict]:
    # Provide all samples to LLM to identify duplicates
    prompt = format_brute_force_history_prompt(task_instructions, reference_objects, objects)
    return lm_service.generate(prompt, output_model)
    

def _deduplicate_last_k(
        objects: list[dict],
        lm_service: LMService,
        task_instructions: str,
        output_model: BaseModel,
        reference_objects: dict = None,
        **kwargs
    ) -> list[dict]:
    # Only check against last K samples
    k = kwargs.get('k', 5)
    unique_objects = []
    for i, obj in enumerate(objects):
        start_idx = max(0, i - k)
        recent_objects = objects[start_idx:i]
        
        if recent_objects:
            prompt = format_last_k_history_prompt(task_instructions, reference_objects, recent_objects, k, obj)
            response = lm_service.generate(prompt, output_model)
            if "no" in response.lower():
                unique_objects.append(obj)
        else:
            unique_objects.append(obj)
            
    return unique_objects

def _deduplicate(
        objects: list[dict],
        strategy: str,
        lm_service: LMService = None,
        vectorizer_service: VectorizerService = None,
        task_instructions: str = None,
        reference_objects: dict = None,
        output_model: BaseModel = None,
        **kwargs
    ) -> list[dict]:
    
    if strategy == "GRAD":
        # NOT TESTED - POC Placeholder
        # Generate, Retrieve and Assess Duplicate (GRAD)
        threshold = kwargs.get('threshold', 0.95)
        vectors = [vectorizer_service.vectorize(obj) for obj in objects]
        
        duplicates = set()
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                similarity = vectors[i].dot(vectors[j])
                if similarity > threshold:
                    # Ask LLM to verify if these are duplicates
                    prompt = f"Are these objects duplicates?\nObj1: {objects[i]}\nObj2: {objects[j]}"
                    response = lm_service.generate(prompt, output_model)
                    if "yes" in response.lower():
                        duplicates.add(j)
                        
        return [obj for i, obj in enumerate(objects) if i not in duplicates]
        
    elif strategy == "clustering":
        # NOT TESTED - POC Placeholder
        # Clustering-based deduplication
        import numpy as np
        from sklearn.manifold import TSNE
        from hdbscan import HDBSCAN
        
        vectors = np.array([vectorizer_service.vectorize(obj) for obj in objects])
        
        # Reduce dimensionality
        tsne = TSNE(n_components=2)
        vectors_2d = tsne.fit_transform(vectors)
        
        # Cluster
        clusterer = HDBSCAN(min_cluster_size=2)
        cluster_labels = clusterer.fit_predict(vectors_2d)
        
        # Keep one sample per cluster
        unique_objects = []
        for cluster_id in set(cluster_labels):
            if cluster_id == -1:  # Noise points
                continue
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            unique_objects.append(objects[cluster_indices[0]])
            
        return unique_objects
    
    return objects
