import os
import random
import re
import json
from pathlib import Path
import openai
import time

import json
import openai

def jsonStringFromFopen(file_path):
    api_ref_string = ""
    inside_json = False
    with open(file_path, 'r', encoding='utf-8', errors='replace') as api_ref_fh:
        for line in api_ref_fh:
            line = line.strip()
            if line.startswith('{'):
                inside_json = True
            elif line.endswith('}'):
                inside_json = False
                api_ref_string += line
                continue
            if inside_json:
                api_ref_string += line + '\n'
    return api_ref_string

def loadDataFromJSON(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def readTxtFile(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    return content

def saveData(data, savePath):
   with open(savePath, 'w') as f:
      for entry in data:
         json.dump(entry, f)
         f.write('\n')

def openaiRequest(prompt):
  retries = 0
  while retries < 5:
      try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                "role": "system",
                "content": "Your task is to write an API request for a new schema given the API reference and an example."
            },
            {
                "role": "user",
                "content": prompt
            }],
            temperature=0,
            max_tokens=4095,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0).choices[0].message.content
        break
      except:
          print("An error from OpenAI occurred. Retrying in 10 seconds...")
          retries += 1
          time.sleep(10)
  return response

openai.api_key = "sk-foobar"

# Might be interesting to also ablate this against chain-of-thought where it thinks and then fixes

# Can visualize the clusters of these explanations in a t-SNE plot

def fixQuery(APIref, schema, failedQuery):
    okFixItPrompt = """
    Can you please fix the following API request?

    An AI model was given the task to write an API request for a custom database schema based on the API reference provided.

    The AI model received this pair of API reference and custom database schema.
    API reference:
    %s
    Custom Database Schema:
    %s
    And outputted the following API request:
    %s
    This API request failed to execute.
    Could you please write the correct API request?

    VERY IMPORTANT!! Please format the request for the CUSTOM SCHEMA! The `Class` name in your API request should align with the Class Name shown in the schema.
    VERY IMPORTANT!! Please do not forget the "... on" syntax when accessing the properties of another Weaviate object linked with a reference such as:
    ... on Author {
        name
    }
    VERY IMPORTANT!! Please note that properties are never accessed with a . syntax such as `className.property`!
    VERY IMPORTANT! Please only output the GraphQL for the query and nothing else!
    VERY IMPORTANT! When writing the GraphQL query, begin with ```graphql and end with ``` to maintain the formatting of example queries.
    """ % (APIref, schema, failedQuery)
    return okFixItPrompt

dataForFiltering = []

counter = 0

queries = loadDataFromJSON("../validatorEngine/failed-WeaviateGorillaGQLDataset.json")

start = time.time()
for example in queries:
    print(counter)
    apiRef = example["apiRef"]
    #APItoQueryExample = readTxtFile("../data/API-to-Query-Examples/"+example["apiRefPath"])
    #APItoCommandExample = readTxtFile("../data/API-to-Command-Examples/"+example["apiRefPath"])
    schema = example["schema"]
    failedQuery = example["output"]
    print(f"FAILED QUERY \n {failedQuery}")
    newQueryPrompt = fixQuery(apiRef, schema, failedQuery)
    newQuery = openaiRequest(newQueryPrompt)
    nlcommand = example["nlcommand"]
    print(f"\n NEW QUERY \n {newQuery} \n")

    inputForGorilla = """
    Your task is to write an API request for a custom database schema based on the API reference provided.

    For guidance on how to correctly format this API request, consult the API reference here:
    Note: Please only use the API reference to understand the syntax of the request. Make sure your request is compliant with it.
    Here are some quick notes about the API syntax:
    - All queries should start with either `Get` or `Aggregate`. A common mistake is to begin the API request with `query`, please do not make this mistake.
    - All queries should begin with an open curly bracket, `{`

    API REFERENCE:
    %s

    CUSTOM SCHEMA:
    %s

    COMMAND:
    %s

    API Request:
    """ % (apiRef, schema, nlcommand)
                
    dataForFiltering.append({
        "input": inputForGorilla,
        "output": newQuery,
        "nlcommand": nlcommand,
        "apiRef": apiRef,
        "apiRefPath": example["apiRefPath"],
        "schema": schema,
        "schemaPath": example["schemaPath"]
    })

    counter += 1
    if counter % 100 == 99:
        print("\n \n \n Save Trigger! \n \n \n ")
        print(f"Saving at step... {counter}")
        saveData(dataForFiltering, f"{counter}-Retry-Gorilla-Queries.json")
        print("\n \n File saved! \n \n")
        print(f"Ran for {time.time() - start} seconds so far.")

saveData(dataForFiltering, f"Retried-WeaviateGorillaDataset.json")
print(f"\n \n Created and saved {counter} Weaviate Gorilla queries in {time.time() - start} seconds.")