from pydantic import BaseModel
from typing import Literal, Union, List

class FilterCondition(BaseModel):
    property: str
    operator: str  # Could be made Literal if we want to restrict operators
    value: Union[str, int, float]  # Supporting multiple value types

class Filter(BaseModel):
    operator: Literal["AND", "OR"] 
    conditions: List[FilterCondition]