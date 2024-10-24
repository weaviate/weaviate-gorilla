import random
import json

def loadData(dataPath):
    data = []
    with open(dataPath, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data

allData = loadData("../data/all-clean-WeaviateGorillaGQLDataset.json")

def splitData(data, trainRatio = 0.8):
    trainSize = int(len(data) * trainRatio)
    trainData = random.sample(data, trainSize)
    testData = [item for item in data if item not in trainData]
    return trainData, testData

# Split all data into 80% train and 20% test
trainData, testData = splitData(allData, 0.8)

# Save data
def saveData(data, savePath):
    with open(savePath, 'w') as f:
        for entry in data:
            json.dump(entry, f)
            f.write('\n')

saveData(trainData, "WithRetrieval-Random-Train-80.json")
saveData(testData, "WithRetrieval-Random-Test-80.json")
