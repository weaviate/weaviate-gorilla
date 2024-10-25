from pydantic import BaseModel
from typing import Literal, Dict, List, Optional

class ParameterProperty(BaseModel):
    type: str
    description: str

class Parameters(BaseModel):
    type: Literal["object"]
    properties: Dict[str, ParameterProperty]
    required: Optional[List[str]]

class Function(BaseModel):
    name: str
    description: str
    parameters: Parameters

class Tool(BaseModel):
    type: Literal["function"]
    function: Function

weaviate_function_calling_schema = [
    Tool(
        type="function",
        function=Function(
            name="get_search_results",
            description="Get search results for a provided query.",
            parameters=Parameters(
                type="object",
                properties={
                    "query": ParameterProperty(
                        type="string",
                        description="The search query.",
                    ),
                    "source": ParameterProperty(
                        type="string",
                        description="The source to search through, either \"DOCS\" or \"CODE\"",
                    ),
                },
                required=["query"],
            ),
        ),
    ),
    Tool(
        type="function",
        function=Function(
            name="get_objects_from_filters",
        )
    )
]

