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
                objects = _deduplicate(
                    objects=objects,
                    strategy=dedup_strategy,
                    lm_service=lm_service,
                    vectorizer_service=vectorizer_service,
                    task_instructions=task_instructions,
                    reference_objects=reference_objects,
                    **dedup_params or {}
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
            
            if len(objects) % 10 == 9:
                objects = _deduplicate(
                    objects=objects,
                    strategy=dedup_strategy,
                    lm_service=lm_service,
                    vectorizer_service=vectorizer_service,
                    task_instructions=task_instructions,
                    reference_objects=reference_objects,
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

def _deduplicate(
        objects: list[dict],
        strategy: str,
        lm_service: LMService = None,
        vectorizer_service: VectorizerService = None,
        task_instructions: str = None,
        reference_objects: dict = None,
        **kwargs
    ) -> list[dict]:
    
    if strategy == "brute_force":
        # Provide all samples to LLM to identify duplicates
        prompt = f"""Given the following task and context:

        Original Task Instructions:
        {task_instructions}

        Reference Objects (if any):
        {reference_objects if reference_objects else 'None'}

        Previously Generated Samples:
        {objects}

        Please analyze these samples carefully and return only the indices (as space-separated numbers) of objects that should be removed due to being duplicates. Consider semantic similarity rather than exact matches, while keeping in mind the original task and reference objects.

        If there are no duplicates, return an empty response."""
        
        response = lm_service.generate(prompt)
        indices_to_remove = [int(idx) for idx in response.split()]
        return [obj for i, obj in enumerate(objects) if i not in indices_to_remove]
        
    elif strategy == "last_k":
        # Only check against last K samples
        k = kwargs.get('k', 5)
        unique_objects = []
        for i, obj in enumerate(objects):
            start_idx = max(0, i - k)
            recent_objects = objects[start_idx:i]
            
            if recent_objects:
                prompt = f"""Given the following task and context:

                Original Task Instructions:
                {task_instructions}

                Reference Objects (if any):
                {reference_objects if reference_objects else 'None'}

                Recent {k} Samples:
                {recent_objects}

                New Sample to Check:
                {obj}

                Please respond with 'true' if this is a duplicate of any recent sample, or 'false' if it is unique. Consider semantic similarity rather than exact matches, while keeping in mind the original task and reference objects."""
                                
                response = lm_service.generate(prompt)
                if "no" in response.lower():
                    unique_objects.append(obj)
            else:
                unique_objects.append(obj)
                
        return unique_objects
        
    elif strategy == "GRAD":
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
                    response = lm_service.generate(prompt)
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
