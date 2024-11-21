# Experiment Results

## NEED TO BE UPDATED!

# NEW DATA

## GPT-4o mini

Total queries analyzed: 315
Successful predictions: 308
Failed predictions: 7
Average AST score: 83.43%

Per schema scores:
Schema 0: 84.14%
Schema 1: 84.10%
Schema 2: 82.30%
Schema 3: 82.23%
Schema 4: 79.18%

Per component analysis:
Queries with search (160): 72.48%
Queries with integer filters (80): 76.31%
Queries with text filters (80): 85.16%
Queries with boolean filters (80): 88.13%
Queries with integer aggregations (80): 82.69%
Queries with text aggregations (80): 78.78%
Queries with boolean aggregations (80): 84.59%
Queries with groupby (160): 80.03%

## GPT-4o

Total queries analyzed: 315
Successful predictions: 304
Failed predictions: 11
Average AST score: 85.66%

Per schema scores:
Schema 0: 87.97%
Schema 1: 85.59%
Schema 2: 85.08%
Schema 3: 81.45%
Schema 4: 82.62%

Per component analysis:
Queries with search (160): 76.77%
Queries with integer filters (80): 79.28%
Queries with text filters (80): 84.53%
Queries with boolean filters (80): 91.44%
Queries with integer aggregations (80): 82.38%
Queries with text aggregations (80): 83.16%
Queries with boolean aggregations (80): 87.03%
Queries with groupby (160): 83.53%


# OLD DATA

## Overall Performance Comparison

| Metric | GPT-4o | GPT-4o-mini |
|--------|--------|-------------|
| Total Queries | 315 | 315 |
| Successful Predictions | 300 | 258 |
| Failed Predictions | 15 | 57 |
| Average AST Score | 75.87% | 64.63% |

## Per Schema Performance

| Schema | GPT-4o | GPT-4o-mini |
|--------|--------|-------------|
| Schema 0 | 79.17% | 61.15% |
| Schema 1 | 70.42% | 62.40% |
| Schema 2 | 78.23% | 73.65% |
| Schema 3 | 74.06% | 66.15% |
| Schema 4 | 73.96% | 58.85% |

## Component Analysis

| Component Type | Sample Size | GPT-4o | GPT-4o-mini |
|---------------|-------------|---------|-------------|
| Search Queries | 160 | 68.17% | 55.00% |
| Integer Filters | 80 | 72.50% | 61.83% |
| Text Filters | 80 | 72.67% | 60.17% |
| Boolean Filters | 80 | 81.58% | 67.25% |
| Integer Aggregations | 80 | 73.58% | 68.58% |
| Text Aggregations | 80 | 74.17% | 66.17% |
| Boolean Aggregations | 80 | 77.92% | 69.50% |
| GroupBy Operations | 160 | 66.50% | 58.37% |

![Weaviate Gorilla](../../visuals/weaviate-gorillas/gorilla-118.png)
