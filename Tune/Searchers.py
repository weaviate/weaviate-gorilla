import typing

class BM25():
    def __init__(self, properties: list, max_limit: int, autocuts=[]):
        print("Constructed BM25 Searcher")
        # parse args into everything to test with a name
        self.searcher_configs = []
        self.limit = max_limit
        # Important hard-coded variable.
        self.queryKey = "DocID"

        # parse configs, issue #7 refactor into helper function
        for property in properties:
            if len(autocuts) > 0:
                for autocut in autocuts:
                    self.searcher_configs.append({
                        "name": "bm25-"+property+"-"+str(autocut), # ToDo, improve name+args parsing - Issue #3.
                        # args is private state custom to each searcher
                        "args": {
                            "property": property,
                            "autocut": autocut
                        }
                    })
                # add one without autocut
                self.configs.append({
                    "name": "bm25-"+property+"-"+str(autocut),
                    "args": {
                        "properties": property
                    }
                })
            else:
                self.configs.append({
                    "name": property,
                    "args": {
                        "properties": property
                    }
                })
        self.num_configs = len(self.configs)
    
    def meta(self):
        return "BM25"
    
    def num_configs(self):
        return self.num_configs
    
    # Chose to separate these in case of dynamic client and collection tuning.
    def set_client_and_collection(self, client):
        self.client = client
    
    def set_collection(self, collection: str):
        self.collection = collection
    
    def set_queries(self, queries: list):
        self.queries = queries
    
    def set_docID_alias(self, docID_alias: str):
        '''
        docID_alias is used to alias the property document id, e.g. `DocID`
        '''
        self.docID_alias = docID_alias
    
    def search(self, max_limit: int):
        all_results = {}
        # init all_results
        for search_config in self.configs:
            all_results[search_config.name] = []
        # Need to parse e.g. "question^2,answer"
        for query in self.queries:
            for search_config in self.configs:
                name = search_config["name"]
                args = search_config["args"]
                results = self.client.get(self.collection, [self.docID_alias])\
                    .with_bm25(
                        query=query["raw_query"],
                        properties=[args.properties],
                        autocut=[args.autocut]
                    )\
                    .with_limit(max_limit).do()
            parsed_ids = [result[self.docID_alias] for result in results["data"][self.collection]["Get"]]
            all_results[search_config.name].append({
                "query_id": query["query_id"],
                "retrieved_ids": parsed_ids
            })
        return all_results

class Vector():
    def __init__(self):
        print("Constructed Vector Searcher")
    
    def meta(self):
        return "Vector"

    def search(self):
        return 0

class Hybrid():
    def __init__(self):
        print("Constructed Hybrid Searcher")
    
    def meta(self):
        return "Hybrid"

    def search(self):
        return 0