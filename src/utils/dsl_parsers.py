import weaviate
from src.models import (
    IntPropertyFilter,
    TextPropertyFilter,
    BooleanPropertyFilter,
    IntAggregation,
    TextAggregation,
    BooleanAggregation,
    GroupBy
)
import re
from typing import Tuple, Union, Any
from pydantic import BaseModel
from typing import Literal, Dict, List, Optional
from weaviate.classes.query import Filter, Metrics
from weaviate.classes.aggregate import GroupByAggregate

def _build_weaviate_filter(filter_string: str) -> Filter:
    def _parse_condition(condition: str) -> Filter:
        parts = condition.split(':')
        if len(parts) < 3:
            raise ValueError(f"Invalid condition: {condition}")
        
        property, operator, value = parts[0], parts[1], ':'.join(parts[2:])
        
        if operator == '==':
            return Filter.by_property(property).equal(value)
        elif operator == '!=':
            return Filter.by_property(property).not_equal(value)
        elif operator == '>':
            return Filter.by_property(property).greater_than(float(value))
        elif operator == '<':
            return Filter.by_property(property).less_than(float(value))
        elif operator == '>=':
            return Filter.by_property(property).greater_than_equal(float(value))
        elif operator == '<=':
            return Filter.by_property(property).less_than_equal(float(value))
        elif operator == 'LIKE':
            return Filter.by_property(property).like(value)
        elif operator == 'CONTAINS_ANY':
            return Filter.by_property(property).contains_any(value.split(','))
        elif operator == 'CONTAINS_ALL':
            return Filter.by_property(property).contains_all(value.split(','))
        elif operator == 'WITHIN':
            lat, lon, dist = map(float, value.split(','))
            return Filter.by_property(property).within_geo_range(lat, lon, dist)
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def _parse_group(group: str) -> Filter:
        if 'AND' in group:
            conditions = [_parse_group(g.strip()) for g in group.split('AND')]
            return Filter.all_of(conditions)
        elif 'OR' in group:
            conditions = [_parse_group(g.strip()) for g in group.split('OR')]
            return Filter.any_of(conditions)
        else:
            return _parse_condition(group)

    # Remove outer parentheses if present
    filter_string = filter_string.strip()
    if filter_string.startswith('(') and filter_string.endswith(')'):
        filter_string = filter_string[1:-1]

    return _parse_group(filter_string)

def _build_weaviate_filter_return_model(filter_string: str):
    def _parse_condition(condition: str):
        parts = condition.split(':')
        if len(parts) < 3:
            raise ValueError(f"Invalid condition: {condition}")
        
        property, operator, value = parts[0], parts[1], ':'.join(parts[2:])
        
        if operator in ['>', '<', '>=', '<=']:
            return IntPropertyFilter(property_name=property, operator=operator, value=float(value))
        elif operator in ['=', '==']:  # Handle both = and == operators
            if value.lower() in ['true', 'false']:
                return BooleanPropertyFilter(property_name=property, operator=operator, value=value.lower() == 'true')
            try:
                return IntPropertyFilter(property_name=property, operator=operator, value=float(value))
            except ValueError:
                return TextPropertyFilter(property_name=property, operator=operator, value=value)
        elif operator == 'LIKE':
            return TextPropertyFilter(property_name=property, operator=operator, value=value)
        elif operator == '!=':
            if value.lower() in ['true', 'false']:
                return BooleanPropertyFilter(property_name=property, operator=operator, value=value.lower() == 'true')
            try:
                return IntPropertyFilter(property_name=property, operator=operator, value=float(value))
            except ValueError:
                return TextPropertyFilter(property_name=property, operator=operator, value=value)
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def _parse_group(group: str):
        # Handle AND/OR groups with parentheses
        if group.startswith('AND(') or group.startswith('OR('):
            operator = group[:3] if group.startswith('AND') else group[:2]
            content = group[group.find('(')+1:group.rfind(')')]
            conditions = []
            
            # Split by comma while respecting nested parentheses
            current = ''
            paren_count = 0
            for char in content:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == ',' and paren_count == 0:
                    conditions.append(_parse_group(current.strip()))
                    current = ''
                    continue
                current += char
            if current:
                conditions.append(_parse_group(current.strip()))
                
            return conditions
        elif 'AND' in group:
            conditions = [_parse_group(g.strip()) for g in group.split('AND')]
            return conditions
        elif 'OR' in group:
            conditions = [_parse_group(g.strip()) for g in group.split('OR')]
            return conditions
        else:
            return _parse_condition(group)

    return _parse_group(filter_string)

def _build_weaviate_aggregation_return_model(agg_string: str) -> Tuple[Optional[GroupBy], List[Union[IntAggregation, TextAggregation, BooleanAggregation]]]:
    """
    Parses an aggregation string into Weaviate GroupBy and Aggregation models.
    
    Format:
    GROUP_BY(property) METRICS(property:type[metrics], property2:type[metrics])
    
    Examples:
    - "GROUP_BY(publication) METRICS(wordCount:int[count,mean,max])"
    - "METRICS(rating:num[mean,sum], title:text[count,topOccurrences])"
    - "GROUP_BY(author) METRICS(isPublished:bool[totalTrue,percentageFalse])"
    
    Returns:
    Tuple of (GroupBy, List[Aggregation])
    """
    def _parse_metrics(metrics_str: str) -> List[Union[IntAggregation, TextAggregation, BooleanAggregation]]:
        # Extract content within METRICS(...)
        metrics_list = []
        
        # Split multiple metrics definitions by comma, but not within brackets
        metrics_parts = []
        current_part = ""
        bracket_count = 0
        
        for char in metrics_str:
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            elif char == ',' and bracket_count == 0:
                metrics_parts.append(current_part.strip())
                current_part = ""
                continue
            current_part += char
        if current_part:
            metrics_parts.append(current_part.strip())
        
        # Parse each metric definition
        for metric in metrics_parts:
            # Parse property:type[operations]
            match = re.match(r'(\w+):(text|int|num|bool)\[([\w,]+)\]', metric.strip())
            if not match:
                raise ValueError(f"Invalid metrics format: {metric}")
            
            prop_name, data_type, operations = match.groups()
            operations = [op.strip() for op in operations.split(',')]
            
            # Create appropriate Aggregation object based on type
            if data_type == 'text':
                metric_obj = TextAggregation(
                    property_name=prop_name,
                    metrics=operations,
                    top_occurrences_limit=None  # Adjust as needed
                )
            elif data_type in ('int', 'num'):
                metric_obj = IntAggregation(
                    property_name=prop_name,
                    metrics=operations
                )
            elif data_type == 'bool':
                metric_obj = BooleanAggregation(
                    property_name=prop_name,
                    metrics=operations
                )
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
            metrics_list.append(metric_obj)
        
        return metrics_list

    def _parse_group_by(group_str: str) -> GroupBy:
        # Extract property name from GROUP_BY(property)
        match = re.match(r'GROUP_BY\((\w+)\)', group_str)
        if not match:
            raise ValueError(f"Invalid GROUP_BY format: {group_str}")
        
        return GroupBy(property_name=match.group(1))

    # Initialize return values
    group_by = None
    metrics = []
    
    # Split into parts by space, but not within parentheses
    parts = []
    current_part = ""
    paren_count = 0
    
    for char in agg_string:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        elif char.isspace() and paren_count == 0:
            if current_part:
                parts.append(current_part)
            current_part = ""
            continue
        current_part += char
    if current_part:
        parts.append(current_part)
    
    # Parse each part
    for part in parts:
        if part.startswith('GROUP_BY'):
            if group_by is not None:
                raise ValueError("Multiple GROUP_BY clauses not allowed")
            group_by = _parse_group_by(part)
        elif part.startswith('METRICS'):
            # Extract content within METRICS(...)
            match = re.match(r'METRICS\((.*)\)', part)
            if not match:
                raise ValueError(f"Invalid METRICS format: {part}")
            metrics.extend(_parse_metrics(match.group(1)))
    
    return group_by, metrics
