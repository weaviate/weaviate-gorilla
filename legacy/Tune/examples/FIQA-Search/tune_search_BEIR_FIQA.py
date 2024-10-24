from Tuner import tune
from Searchers import BM25, Vector, Hybrid
from Searcher_Metrics import SearchRecall, SearchPrecision, SearchWinsLLM
import weaviate

search_tuner = tune(
    weaviate_client=weaviate.Client("http://localhost:8080"),
    collection="Document",
    query="queries.json",
    numQueries=100   
)

search_tuner.search(
    searchers=[
        BM25(properties=["content"]),
        Vector,
        Hybrid(alphas=[0.5, 0.75], properties=["content"])
    ],
    search_metrics=[
        SearchRecall, SearchPrecision, SearchWinsLLM
    ],
    limits=[100,20,5,1]
).do()