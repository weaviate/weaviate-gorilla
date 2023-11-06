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
master = loadDataFromJSON("../data/all-clean-WeaviateGorillaGQLDataset.json")

withoutRetrievalPromptDataset = []

def formatInput(schema, nlcommand):
    inputForGorilla = """
    Your task is to write an API request for a custom database schema based on the API reference provided.

    For guidance on how to correctly format this API request, consult the API reference here:
    Note: Please only use the API reference to understand the syntax of the request. Make sure your request is compliant with it.
    Here are some quick notes about the API syntax:
    - All queries should start with either `Get` or `Aggregate`. A common mistake is to begin the API request with `query`, please do not make this mistake.
    - All queries should begin with an open curly bracket, `{`

    CUSTOM SCHEMA:
    %s

    COMMAND:
    %s

    API Request:
    """ % (schema, nlcommand)
    return inputForGorilla

# append new data to master
for row in master:
    schema = row["schema"]
    nlcommand = row["nlcommand"]
    inputForWithoutRetrievalGorilla = formatInput(schema, nlcommand)
    withoutRetrievalPromptDataset.append({
        "input": inputForWithoutRetrievalGorilla,
        "output": row["output"],
        "nlcommand": nlcommand,
        "apiRef": row["apiRef"],
        "apiRefPath": row["apiRefPath"],
        "schema": schema,
        "schemaPath": row["schemaPath"]
    })

# save master with a new filename
saveData(withoutRetrievalPromptDataset, "withoutRetrieval-WeaviateGorillaGQLDataset.json")
print(len(withoutRetrievalPromptDataset))
# Note, the retryEngine will need this as well with the fixed queries