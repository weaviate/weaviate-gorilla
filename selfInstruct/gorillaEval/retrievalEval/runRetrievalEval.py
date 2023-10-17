import weaviate
import json
import time

WeaviateGorillaDataset = []
with open('../dataEngine/data/WeaviateGorillaDataset.json', 'r') as f:
    for line in f:
        WeaviateGorillaDataset.append(json.loads(line.strip()))

def parseCommand(rawCommandStr):
    prefix = "```text\n"
    if rawCommandStr.startswith(prefix):
        removedBackticks = rawCommandStr[len(prefix):]
    removedBackticks = removedBackticks[:-5] # remove end backticks
    removedBackticks = removedBackticks.replace("`", "")
    removedBackticks = removedBackticks.strip()
    removedBackticks = removedBackticks.replace("\"", "'")
    removedBackticks = removedBackticks.replace("\n", "")
    removedBackticks = removedBackticks.replace("\\", "")
    return removedBackticks

client = weaviate.Client("http://localhost:8080")

# Get nearText results
def getNearTextResults(query):
    templatedQuery = """
    {
        Get {
            APIReference(
                nearText: {
                    concepts: ["%s"]
                },
                limit: 10
            ){
                content
                apiRefPath
            }
        }
    }                        
    """ % query
    response = client.query.raw(templatedQuery)
    return response

#def getBM25TextResults(query):

#def getHybridTextResults(query):

#def getNearTextWithRerankResults(query):
def getNearTextWithRerankResults(query):
    templatedQuery = """
    {
        Get {
            APIReference(
                nearText: {
                    concepts: ["%s"]
                },
                limit: 10
            ){
                content
                apiRefPath
                _additional {
                    rerank(
                        query: "%s"
                        property: "content"
                    ){
                    score
                    }
                }
            }
        }
    }                        
    """ % (query, query)
    response = client.query.raw(templatedQuery)
    return response

#def getBM25WithRerankResults(query):

def getHybridWithRerankResults(query):
    templatedQuery = """
    {
        Get {
            APIReference(
                hybrid: {
                    query: "%s"
                },
                limit: 10
            ){
                content
                apiRefPath
                _additional {
                    rerank(
                        query: "%s"
                        property: "content"
                    ){
                    score
                    }
                }
            }
        }
    }                        
    """ % (query, query)
    response = client.query.raw(templatedQuery)
    return response

# Evaluate results -- this should be one function
def evaluateResults(response, groundTruthAPIRef):
    for idx, dataObject in enumerate(response["data"]["Get"]["APIReference"]):
        if dataObject["apiRefPath"] in groundTruthAPIRef:
            return idx+1
    return 11 # limit all searches to 10 results

recall_scores = {}
for idx, nlCommandAPIPair in enumerate(WeaviateGorillaDataset):
    if idx % 50 == 49:
        break
    
    commandFromFile, groundTruth = nlCommandAPIPair["nlcommand"], nlCommandAPIPair["apiRefPath"]
    command = parseCommand(commandFromFile)
    searchResults = getHybridWithRerankResults(command)
    foundAPIAt = evaluateResults(searchResults, groundTruth)
    print(foundAPIAt)
    if groundTruth in recall_scores.keys():
        recall_scores[groundTruth].append(foundAPIAt)
    else:
        recall_scores[groundTruth] = [foundAPIAt]
    time.sleep(10) # Avoid rate limit

# Visualizing the distribution of found positions for all APIs
import matplotlib.pyplot as plt
import numpy as np
all_positions = [pos for positions in recall_scores.values() for pos in positions]
plt.figure()
plt.hist(all_positions, bins=range(1, 12), align='left', rwidth=0.8)
plt.xlabel("Found At Position")
plt.ylabel("Frequency")
plt.title("Distribution of Found Positions Across All APIs")
plt.show()

# Calculating and visualizing the average found position for each API
api_names = list(recall_scores.keys())
average_positions = [np.mean(positions) for positions in recall_scores.values()]

plt.figure()
plt.barh(api_names, average_positions, align='center')
plt.xlabel("Average Found At Position")
plt.ylabel("API Names")
plt.title("Average Found Position for Each API")
plt.show()