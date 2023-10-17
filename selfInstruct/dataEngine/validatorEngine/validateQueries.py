import json
import re
import weaviate

''' Utils '''

def loadDataFromJSON(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def json_reader(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as api_ref_fh:
        data = json.load(api_ref_fh)
    return data

# Load Data
responses = loadDataFromJSON("./failed-RETRIED-WeaviateGorillaGQLDataset.json")
# Connect to Weaviate
client = weaviate.Client("http://localhost:8080")

def didItExecute(WeaviateClient, schemaPath, modelOutput):
    WeaviateClient.schema.delete_all()
    schema = json_reader(f'../../dataEngine/data/ToySchemas/{schemaPath}')
    WeaviateClient.schema.create(schema)
    print("Created Schema \n")
    WeaviateResponse = client.query.raw(modelOutput)
    return WeaviateResponse
    # check keys of Weaviate Response

def extract_graphql_code(text):
    pattern = r'```graphql(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if (len(matches) > 0):
        return matches[0]
    else:
        return text # query did not start / end with ```graphql / ```

counter = 1
successfulQueries = []
failedQueries = []
failedAPIsCount = {}
failedSchemasCount = {}
for example in responses:
    if "readme" not in example["schemaPath"]:
        print(f"Evaluating query: {counter}")
        counter += 1
        print("\n")
        print("Schema = " + example["schemaPath"])
        print("\n")
        modelQuery = extract_graphql_code(example["output"])
        print("Query \n")
        print(modelQuery)
        print("\n")
        weaviateResponse = didItExecute(client, example["schemaPath"], modelQuery)
        if "errors" in weaviateResponse.keys():
            print("FAILED! FAILED! FAILED! \n")
            failedQueries.append(example)
            # Update failed Schema tracker
            if example["schemaPath"] in failedSchemasCount.keys():
                failedSchemasCount[example["schemaPath"]] += 1
            else:
                failedSchemasCount[example["schemaPath"]] = 1
            # Update API tracker
            if example["apiRefPath"] in failedAPIsCount.keys():
                failedAPIsCount[example["apiRefPath"]] += 1
            else:
                failedAPIsCount[example["apiRefPath"]] = 1
        else:
            successfulQueries.append(example)

print(f"{len(successfulQueries)} Queries successfully executed!")
print(f"{len(failedQueries)} Queries failed to execute!")

def saveData(data, savePath):
   with open(savePath, 'w') as f:
      for entry in data:
         json.dump(entry, f)
         f.write('\n')

saveData(successfulQueries, "clean-RETRY-WeaviateGorillaGQLDataset.json")
saveData(failedQueries, "failed-RETRY-WeaviateGorillaGQLDataset.json")

print("FAILED API Count \n")
print(failedAPIsCount)
print("FAILE SCHEMA COUNT \n")
print(failedSchemasCount)