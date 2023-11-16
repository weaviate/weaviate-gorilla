import typing

class SearchRecall():
    # Issue #4, better organize public and private state
    def __init__(self):
        print("Constructed SearchRecall Metric")
        
    def meta(self):
        return "search-recall"
    
    def set_limits(self, limits: list):
        self.limits = limits

    def set_query_collection(self, query_collection):
        '''
        query_collection data schema: List{}
        {
            "id": int
            "query": str,
            "ground_truth": []int
        }
        '''
        self.query_collection = query_collection

    def set_results(self, results: list):
        ### Use internal state of limits []int
        '''
        ### Issue #2, incomplete schema hierarchy
        results Schema, List{}
        {
            "searcher": "bm25",
            "query_id": 1
            "ids": [14, 5, 3, ...]
        }
        '''
        self.results = results
        searcher_results = []
        for result in self.results:
            local_result = 0
            for limit in self.limits:
                truncated_results = result[:limit]
                for result in truncated_results:
                    if result in self.ground_truth

                


    def calculate_metric(self):
        '''
        recall per limit
        return:
        {
            "limit": 100,
            "score": 30.8
        },
        {
            "limit": 20,
            "score": 20.6
        },
        {
            "limit": 1,
            "score": 7
        }
        '''

class SearchPrecision():
    def __init__(self):
        print("Constructed SearchPrecision Metric")
    
    def meta(self):
        return "search-precision"

    def calculate_metric():
        return 0

class SearchWinsLLM():
    def __init__(self):
        print("Constructed SearchWinsLLM Metric")
    
    def meta(self):
        return "search-wins-llm"

    def calculate_metric():
        return 0

def initSearchMetrics(searcher_metrics):
    return 0, 0
