import os
import random
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
  VERY IMPORTANT! Please only output the GraphQL for the query and nothing else! Please begin the GraphQL query with ```graphql and end it with ```.
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

gorillaGQLTrain_SchemaSplit = []
gorillaGQLTest_SchemaSplit = []

gorillaGQLTrain_APISplit = []
gorillaGQLTest_APISplit = []

train_schemas, test_schemas = get_train_test_split_from_filepath("./APIref/", 80)
train_apis, test_apis = get_train_test_split_from_filepath("./ToySchemas/", 80)

for api_ref_path in os.listdir("./APIref"):
  for schema_path in os.listdir("./ToySchemas"):
    api_ref = json_string_from_fopen("./APIref/"+api_ref_path)
    schema = json_string_from_fopen("./ToySchemas/"+schema_path)
    customQuery = generate_query(api_ref, schema)
    print(f"GENERATED QUERY \n \n \n {customQuery} \n")
    nlcommand = query_to_command(api_ref, schema, customQuery)
    inputForGorilla = """Your task is to write an API request for a new schema given the API reference and an example.
    The user command is:
    %s
    Here is the API reference for a query that will help with this command and an example of how to use it:
    %s
    Could you please formulate this query for the following schema?
    %s
    VERY IMPORTANT! Please only output the GraphQL for the query and nothing else!
    """ % (nlcommand, api_ref, schema)

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
