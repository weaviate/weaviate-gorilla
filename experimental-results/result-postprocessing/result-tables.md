# Experiment Results

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

![Weaviate Gorilla](./visuals/weaviate-gorillas/gorilla-124.png)