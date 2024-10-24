from utils import openaiRequset, readJSON
from Indexer_Metrics import initIndexMetrics
from Searcher_Metrics import initSearchMetrics

class tune():
    def __init__(self, client, collection, queries, numQueries):
        ### Handle client
        self.client = client
        ### Handle collection
        # Check if collection is in the Weaviate instance and if there is data in it.
        self.collection = collection
        ### Handle queryCollection
        if queries.endswith(".json"):
            self.queries = readJSON(queries)
        '''
        queryCollection data Schema: List{}
        {
            "id": int,
            "query": str
            "ground_truth": list
        }
        '''
       ### Handle numQueries
        self.numQueries = numQueries

        ### Init with .index()
        self.indexers = []
        self.index_metrics = []
        ### Init with .search()
        self.searchers = []
        self.search_metrics = []
        ### Init with .qa()
        self.controllers = []
        self.qa_metrics = []
        
    
    def index(self, indexers, index_metrics, index_limits):
        self.indexers = indexers
        for indexer in self.indexers:
            self.indexer.set_client(self.client)
        self.index_metrics = index_metrics
        self.index_limits = index_limits
        print("Index parameters set.")
    
    def search(self, searchers, search_metrics, search_limits):
        self.searchers = searchers
        for searcher in self.searchers:
            searcher.set_client(self.client)
            searcher.set_collection(self.collection)
            searcher.set_queries(self.queries)
        self.search_metrics = search_metrics
        for search_metric in self.search_metrics:
            search_metric.set_queries(self.queries)
        self.search_limits = search_limits
        print("Search parameters set.")

    def qa(self, controllers, qa_metrics, qa_limits):
        self.controllers = controllers
        self.qa_metrics = qa_metrics
        self.qa_limits = qa_limits
        print("QA parameters set.")

    def do(self):
        print("Starting evaluation...")
        print("Running index tests...")
        indexMetricsDict, indexMetricFuncs = initIndexMetrics(self.indexer_metrics, self.indexers)
        searcherMetricsDict, searcherMetricFuncs = initSearchMetrics(self.searcher_metrics, self.searchers)
        metric_dict = {}

        ## Note, only running search evaluation so far.
        
        for searcher in self.searchers:
            searcher_results = searcher.search()
            '''
            for example,
            search_results = {
                "bm25-autocut-1": [
                    {
                        query_id: 0,
                        retrieved_ids: [1,2,3,...]
                    },
                    {
                        query_id: 1,
                        retrieved_ids: [2,4,6,...]
                    }
                ],
                "bm25-autocut-2": ...
            }

            ### Return

            "bm25-autocut-1": [
                "recall": 30.5,
                ...
            ],
            "bm25-autocut-2": [
                "recall": 28.4,
                ...
            ]
            '''
            for searcher_name in searcher_results.keys():
                searcher_metrics = {}
                metrics_input = []
                for query in self.queries:
                    for searcher_name in searcher_results.keys():
                        for result in searcher_results[searcher_name]:
                            if query["query_id"] == result["query_id"]:
                                joined_dict = {}
                                joined_dict["query_id"] = query["query_id"]
                                joined_dict["ground_truths"] = query["ground_truths"]
                                joined_dict["retrieved_ids"] = result[["retrieved_ids"]]
                                metrics_input.append(joined_dict)
                
                metric_results = []
                for metric in self.search_metrics:
                    # Issue #10, for LLM Eval you need the Query and the TEXT of the retrieved results...
                    score = metric.calculate_score(metrics_input)
                    metric_results[self.search_metrics.meta()] = score
                metric_dict[searcher_name] = metric_results
        
        return metric_dict



