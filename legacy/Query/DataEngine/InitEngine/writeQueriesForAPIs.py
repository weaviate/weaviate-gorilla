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


def generateQuery(apiRef, taskExample, schema):
  return """
  Your task is to write an API request for a custom database schema based on the API reference provided.
  You do not have an instruction or natural language command to guide you; your goal is to generate a representative API request that could be useful for someone using this custom database schema.

  For guidance on how to correctly format this API request, consult the API reference here:
  Note: Please only use the API reference to understand the syntax of the request. Make sure your request is compliant with it.
  Here are some quick notes about the API syntax:
  - All queries should start with either `Get` or `Aggregate`. A common mistake is to begin the API request with `query`, please do not make this mistake.
  - All queries should begin with an open curly bracket, `{`
  

  Here is an example of adapting API references to a custom schema:

  API REFERENCE:

  %s

  Here is an example of the task you need to perform:
 
  %s

  Please use this example to combine the following API request and CUSTOM SCHEMA:

  Refer to the following schema to adapt the API request to THIS CUSTOM DATABASE SCHEMA:
  CUSTOM SCHEMA:
  %s

  VERY IMPORTANT!! Please format the request for the CUSTOM SCHEMA! The `Class` name in your API request should align with the Class Name shown in the schema.
  VERY IMPORTANT!! Please do not forget the "... on" syntax when accessing the properties of another Weaviate object linked with a reference such as:
  ... on Author {
    name
  } 
  VERY IMPORTANT! Please only output the GraphQL for the query and nothing else!
  VERY IMPORTANT! When writing the GraphQL query, begin with ```graphql and end with ``` to maintain the formatting of example queries.
  """ % (apiRef, taskExample, schema)

def customQueryToCommand(taskExample, apiRef, custom_query):
  return """
  Your task is to understand when a user with a custom database schema would want to use a provided API REFERENCE and a custom query generated in the previous task.
  
  Here is an example of translating custom queries into a natural language command.

  %s

  Please use this example to translate the following custom query into a natural language command.
  Please also use the API Reference for more information on what the query does.

  API REFERENCE:
  %s 

  Custom Query:
  %s

  Please write a natural language command to invoke the custom query.
  Please only output the natural language command, NOT THE API ITSELF, please begin the command with ```text and end it with ``` for the sake of parsing your response.
  """ % (taskExample, apiRef, custom_query)


def reflexion(prompt, response):
    return """
    Please read the following instruction and response very carefully to evaluate if the response follows the instruction exactly.

    Instruction:

    %s
    
    Response:
    
    %s

    Did the response exactly follow the instruction?

    If yes, please output 1.
    If no, please output 0.
    Please air on the side of caution, if there is any doubt that the response exactly followed the instruction, please output 0.
    """ % (prompt, response)

def reflectAndCorrect(prompt, response):
    return """
    The following response was flagged for not exactly following the instruction.
    Please read the following instruction and response very carefully to evaluate if the response follows the instruction exactly.

    Instruction:

    %s

    Response:

    %s

    Please output only the corrected response that follows the Instruction exactly.
    All information needed to correct the response is contained in the original Instruction.
    """

def extractGraphql(s):
    pattern = r'```graphql(.*?)```'
    matches = re.findall(pattern, s, re.DOTALL)

    return matches[0] if matches else None

def ensureStartWithBrace(s):
    # Remove leading/trailing whitespace
    s = s.strip()
    
    # If the string starts with "query", remove it and strip any extra whitespace
    if s.startswith("query"):
        s = s[len("query"):].strip()
    
    # If the string doesn't start with "{", prepend it
    if not s.startswith("{"):
        s = "{" + s

    return s

dataForFiltering = []

counter = 0

print("START OF FILE READING!")
start = time.time()
for apiPath in os.listdir("../data/APIref"):
    if "DS_Store" not in apiPath:
        apiRef = readTxtFile("../data/APIref/"+apiPath)
        APItoQueryExample = readTxtFile("../data/API-to-Query-Examples/"+apiPath)
        APItoCommandExample = readTxtFile("../data/API-to-Command-Examples/"+apiPath)

        for schemaPath in os.listdir("../data/NewSchemas"):
            if "DS_Store" not in schemaPath:
                schema = jsonStringFromFopen("../data/NewSchemas/"+schemaPath)
                newQueryPrompt = generateQuery(apiRef, APItoQueryExample, schema)
                newQuery = openaiRequest(newQueryPrompt)
                print(f"\n {newQuery} \n")
                nlcommandPrompt = customQueryToCommand(APItoCommandExample, apiRef, newQuery)
                nlcommand = openaiRequest(nlcommandPrompt)
                print(f"\n {nlcommand} \n")

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
                    "apiRefPath": apiPath,
                    "schema": schema,
                    "schemaPath": schemaPath
                })

                counter += 1
                if counter % 500 == 499:
                    print("\n \n \n Save Trigger! \n \n \n ")
                    print(f"Saving at step... {counter}")
                    saveData(dataForFiltering, f"DataForFiltering-{counter}.json")
                    print("\n \n File saved! \n \n")
                    print(f"Ran for {time.time() - start} seconds so far.")

saveData(dataForFiltering, f"NewSchemas-WeaviateGorillaDataset.json")
print(f"\n \n Created and saved {counter} Weaviate Gorilla queries in {time.time() - start} seconds.")