import json

def loadDataFromJSON(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def saveData(data, savePath):
   with open(savePath, 'w') as f:
      for entry in data:
         json.dump(entry, f)
         f.write('\n')

# read in master
master = []

# read in new data
newData = loadDataFromJSON("../initEngine/all-WeaviateGorillaDataset.json")

# append new data to master
for row in newData:
    # might have left the forumns.json, professionalnetworking.json, storms in there...
    if row["schemaPath"] == "paintings.json":
        print("Do nothing")
    else:
        master.append(row)

# save master with a new filename
saveData(master, "cleaned-WeaviateGorillaDataset.json")
print(len(master))
# Note, the retryEngine will need this as well with the fixed queries
