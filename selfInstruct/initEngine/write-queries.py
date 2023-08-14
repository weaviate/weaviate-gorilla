import os
import random
import re
import json
from pathlib import Path
import openai

openai.api_key = "sk-foobar"

def openai_request(prompt):
  return openai.ChatCompletion.create(
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

def generate_query(api_ref, schema):
  prompt_template = """Your task is to write an API request for a new schema given the API reference and an example.
  Here is the API reference and example:
  %s
  Could you please formulate this query for the following schema?
  %s
  VERY IMPORTANT! Please only output the GraphQL for the query and nothing else!
  VERY IMPORTANT! Please begin the GraphQL with ```graphql and end it with ``` as shown in the formatting of example queries.
  """ % (api_ref, schema)
  return openai_request(prompt_template)

def query_to_command(api_ref, schema, custom_gql_query):
  # do this
  prompt_template = """Your task is to write a natural language command you would expect from a user that wants to execute this query.
  The Query is for the following API:
  %s
  The Query is for the following Schema:
  %s
  This is the Query:
  %s
  Can you please write a natural language command you would expect from a user that wants to execute this query?
  """ % (api_ref, schema, custom_gql_query)
  return openai_request(prompt_template)

def get_train_test_split_from_filepath(dir, train_pct):
   train_paths, test_paths = [], []
   all_files = os.listdir(dir)
   random.shuffle(all_files)
   num_train_samples = int(len(all_files) * train_pct / 100)
   train = all_files[:num_train_samples]
   test = all_files[num_train_samples:]
   return train, test
      

def json_string_from_fopen(file_path):
    api_ref_string = ""
    inside_json = False
    # Use a context manager to ensure the file gets closed after reading.
    # Set the encoding explicitly and use 'replace' for error handling.
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

def saveData(data, savePath):
   with open(savePath, 'w') as f:
      for entry in data:
         json.dump(entry, f)
         f.write('\n')

def extract_graphql(s):
    pattern = r'```graphql(.*?)```'
    matches = re.findall(pattern, s, re.DOTALL)

    return matches[0] if matches else None

def ensure_start_with_brace(s):
    # Remove leading/trailing whitespace
    s = s.strip()
    
    # If the string starts with "query", remove it and strip any extra whitespace
    if s.startswith("query"):
        s = s[len("query"):].strip()
    
    # If the string doesn't start with "{", prepend it
    if not s.startswith("{"):
        s = "{" + s

    return s

gorillaGQLTrain_SchemaSplit = []
gorillaGQLTest_SchemaSplit = []

gorillaGQLTrain_APISplit = []
gorillaGQLTest_APISplit = []

train_schemas, test_schemas = get_train_test_split_from_filepath("./APIref/", 80)
train_apis, test_apis = get_train_test_split_from_filepath("./ToySchemas/", 80)

counter = 0
for api_ref_path in os.listdir("./APIref"):
  for schema_path in os.listdir("./ToySchemas"):
    api_ref = json_string_from_fopen("./APIref/"+api_ref_path)
    schema = json_string_from_fopen("./ToySchemas/"+schema_path)
    customQuery = ensure_start_with_brace(extract_graphql(generate_query(api_ref, schema)))
    print(f"GENERATED QUERY \n \n \n {customQuery} \n")
    nlcommand = query_to_command(api_ref, schema, customQuery)
    print(f"FOR THE COMMAND: {nlcommand}")
    print(f"\n COUNTER: {counter} \n")
    inputForGorilla = """Your task is to translate a user command into an API request for a database schema given the API reference and an example.
    Here is the API reference and example:
    %s
    The user command is:
    %s
    Could you please formulate this query for the following schema?
    %s
    VERY IMPORTANT! Please only output the GraphQL for the query and nothing else!
    Please begin the GraphQL query with ```graphql and end it with ``` as shown in the formatting of example queries.
    """ % (api_ref, nlcommand, schema)

    if schema_path in train_schemas:
       gorillaGQLTrain_SchemaSplit.append({
          "input": inputForGorilla,
          "output": customQuery
       })
    else:
       gorillaGQLTest_SchemaSplit.append({
          "input": inputForGorilla,
          "output": customQuery
       })
    
    if api_ref_path in train_apis:
       gorillaGQLTrain_APISplit.append({
          "input": inputForGorilla,
          "output": customQuery
       })
    else:
       gorillaGQLTest_APISplit.append({
          "input": inputForGorilla,
          "output": customQuery
       })
    
    counter += 1
    if counter % 10 == 9:
       print(f"Saving at step... {counter}")
       saveData(gorillaGQLTrain_SchemaSplit, f"weaviateGorillaTrain-schemaSplit-{counter}.jsonl")
       saveData(gorillaGQLTest_SchemaSplit, f"weaviateGorillaTest-schemaSplit-{counter}.jsonl")
       saveData(gorillaGQLTrain_APISplit, f"weaviateGorillaTrain-apiSplit-{counter}.jsonl")
       saveData(gorillaGQLTest_APISplit, f"weaviateGorillaTest-apiSplit-{counter}.jsonl")





with open('weaviateGorillaTrain-schemaSplit.jsonl', 'w') as f:
    for entry in gorillaGQLTrain_SchemaSplit:
        json.dump(entry, f)
        f.write('\n')

with open('weaviateGorillaTest-schemaSplit.jsonl', 'w') as f:
    for entry in gorillaGQLTest_SchemaSplit:
        json.dump(entry, f)
        f.write('\n')

with open('weaviateGorillaTrain-apiSplit.jsonl', 'w') as f:
    for entry in gorillaGQLTrain_APISplit:
        json.dump(entry, f)
        f.write('\n')

with open('weaviateGorillaTest-apiSplit.jsonl', 'w') as f:
    for entry in gorillaGQLTest_APISplit:
        json.dump(entry, f)
        f.write('\n')