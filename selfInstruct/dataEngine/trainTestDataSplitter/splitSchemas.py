import random
import json
import os

def loadData(dataPath):
    data = []
    with open(dataPath, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data

allData = loadData("../data/withoutRetrieval-WeaviateGorillaGQLDataset.json")

WeaviateGraphQLAPIs = []

# loop through APIs
for schemaPath in os.listdir("../data/ToySchemas"):
    WeaviateGraphQLAPIs.append(schemaPath)

def splitData(data, trainRatio):
    trainSize = int(len(data) * trainRatio)
    trainData = random.sample(data, trainSize)
    testData = [item for item in data if item not in trainData]
    return trainData, testData

trainAPIPaths, testAPIPaths = splitData(WeaviateGraphQLAPIs, 0.2)

trainAPIs, testAPIs = [], []

for WeaviateGorillaGraphQLExample in allData:
    if WeaviateGorillaGraphQLExample["schemaPath"] in trainAPIPaths:
        trainAPIs.append(WeaviateGorillaGraphQLExample)
    else:
        testAPIs.append(WeaviateGorillaGraphQLExample)

# only save "input" and "output" keys
def saveData(data, savePath):
   with open(savePath, 'w') as f:
      for entry in data:
         json.dump(entry, f)
         f.write('\n')

saveData(trainAPIs, "WithoutRetrieval-SchemaSplit-Train-20.json")
saveData(testAPIs, "WithoutRetrieval-SchemaSplit-Test-20.json")