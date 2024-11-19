# Abstract Syntax Tree Metric Explanation

### High-level

Imagine we're comparing two API calls for processing a customer order: processOrder(totalAmount=99.99, itemCount=3, isExpedited=true) with processOrder(totalAmount=49.99, itemCount=1, isExpedited=false). When we use an Abstract Syntax Tree (AST) to compare these function calls, it's like having a smart order processing system that understands the business logic behind each parameter. The AST breaks down the function calls into a structured tree where each parameter has different significance - changes in totalAmount might be more significant for business logic (affecting payment processing, fraud checks, and shipping insurance) than changes in isExpedited (which only affects shipping method). So when we calculate the similarity between these two orders, we're not just doing simple numerical comparisons. For instance, the difference between a $99.99 order and a $49.99 order might be weighted more heavily (0.4 of our similarity score) because it crosses important business thresholds, while the difference in expedition status might be weighted less (0.2 of our score) since it's a simpler boolean flag. This matches real-world scenarios where certain parameter differences have more far-reaching implications for how the function behaves - just like how in your Weaviate query comparison code, differences in core filters are weighted more heavily (0.25) than differences in grouping options (0.1).

# SQL Query Similarity Scoring Using Abstract Syntax Trees
## Technical Report

### Executive Summary
This report outlines a methodology for comparing SQL queries using Abstract Syntax Tree (AST) scoring, specifically in an educational context where student submissions need to be evaluated against expert solutions. The proposed scoring system provides an objective measure of query similarity while accounting for syntactic variations that may be functionally equivalent.

### Background
SQL queries can be semantically equivalent despite having different syntactic structures. Traditional string-based comparison methods often fail to capture these equivalences. Abstract Syntax Trees provide a structured representation that better captures the logical structure of queries, making them ideal for similarity comparisons.

### Methodology

#### 1. AST Generation
Both the expert (ground truth) and student queries are parsed into their respective ASTs. Each AST represents the query's structure as a hierarchical tree where:
- Nodes represent SQL operations (SELECT, FROM, WHERE, etc.)
- Child nodes represent nested operations and conditions
- Leaf nodes represent specific values, column names, and operators

#### 2. Tree Comparison Algorithm
The scoring algorithm traverses both trees simultaneously, calculating similarity scores at each level:

```python
def calculate_ast_similarity(expert_ast, student_ast):
    # Base similarity score is 100
    base_score = 100
    
    # Weights for different components
    weights = {
        'select_clause': 0.3,
        'from_clause': 0.2,
        'where_clause': 0.25,
        'join_operations': 0.15,
        'order_group': 0.10
    }
    
    final_score = 0
    
    for component, weight in weights.items():
        component_similarity = compare_nodes(
            expert_ast[component],
            student_ast[component]
        )
        final_score += component_similarity * weight * base_score
        
    return final_score
```

#### 3. Scoring Components

1. **Structural Similarity (40%)**
   - Correct clause ordering
   - Matching operation types
   - Proper nesting levels

2. **Node Content Similarity (40%)**
   - Matching column names
   - Equivalent conditions
   - Identical table references

3. **Optional Elements (20%)**
   - Alias usage
   - Comment presence
   - Formatting consistency

### Example Comparison

**Expert Query:**
```sql
SELECT 
    e.employee_id,
    e.first_name,
    d.department_name
FROM 
    employees e
    INNER JOIN departments d ON e.department_id = d.department_id
WHERE 
    e.salary > 50000
ORDER BY 
    e.employee_id;
```

**Student Query:**
```sql
SELECT 
    employees.employee_id,
    employees.first_name,
    departments.department_name
FROM 
    employees
    JOIN departments 
    ON employees.department_id = departments.department_id
WHERE 
    employees.salary > 50000
ORDER BY 
    employee_id;
```

**Scoring Breakdown:**
1. Structure: 40/40
   - All major clauses present and correctly ordered
   - Proper join relationship established

2. Content: 35/40
   - Correct column references (-0)
   - Equivalent join condition (-0)
   - Missing table aliases (-5)

3. Optional Elements: 15/20
   - Different alias usage (-3)
   - Less consistent formatting (-2)

Total Score: 90/100

### Advantages of AST Scoring

1. **Flexibility**
   - Recognizes equivalent queries written in different styles
   - Accommodates varying levels of SQL expertise

2. **Objectivity**
   - Provides consistent scoring across submissions
   - Reduces grader bias

3. **Granularity**
   - Identifies specific areas for improvement
   - Enables detailed feedback

### Limitations and Considerations

1. **Performance Equivalence**
   - AST scoring may not capture query performance differences
   - Optimal query plans may differ despite structural similarity

2. **Semantic Equivalence**
   - Different approaches might produce identical results
   - Need to consider multiple valid solutions

3. **Implementation Complexity**
   - Requires robust SQL parsing
   - Must handle various SQL dialects

### Recommendations for Implementation

1. **Parsing Framework**
   - Use established SQL parsing libraries
   - Implement dialect-specific adjustments

2. **Scoring Weights**
   - Adjust component weights based on query complexity
   - Consider course-specific requirements

3. **Feedback Generation**
   - Provide detailed breakdowns of scores
   - Include specific improvement suggestions

### Conclusion
AST-based scoring provides a robust framework for evaluating SQL query similarity in educational contexts. The method balances the need for objective assessment with the reality that multiple valid solutions may exist. Implementing this scoring system can significantly improve the consistency and fairness of SQL query evaluation while providing valuable feedback to students.
