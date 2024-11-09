from src.models import WeaviateQuery
from src.models import (
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation,
    GroupBy
)
from src.models import Tool, Function, Parameters, ParameterProperty
from src.utils.weaviate_fc_utils import get_collections_info
from src.lm.lm import LMService
from pydantic import BaseModel
from typing import Optional, Any
import json

with open("../data/synthetic-weaviate-queries.json", "r") as json_file:
    weaviate_queries = json.load(json_file)