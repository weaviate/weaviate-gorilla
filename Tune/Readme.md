# Tune

Tune is a RAG Evaluation library customized to Weaviate!

Tune is designed for modular and end-to-end evaluation of RAG pipelines, allowing you to answer questions such as:
1. What is the change in recall from using 32 segments for PQ instead of 4?
2. What is the difference between vector, bm25, and hybrid search?

As well as... combining experiments such as 1 and 2!

Here are some examples:

```python
import Tune
from Tune.searchers import BM25, Vector, Hybrid
from Tune.metrics import SearchRecall, SearchPrecision, SearchWinsLLM

DocTuner = Tune(
  collection="Document",
  queryCollection="queries.json",
  numQueries=100
)

DocTuner.search(
	searchers(
		BM25(properties=["content"]),
		Vector(),
		Hybrid(alphas=[0.5])
	),
	metrics(
		SearchRecall, SearchPrecision, SearchWinsLLM
	)
).do()
```
