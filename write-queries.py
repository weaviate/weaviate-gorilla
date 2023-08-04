import os
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

def json_string_from_fopen(file_path):
  api_ref_fh = open(file_path)
  api_ref = api_ref_fh.readlines()
  api_ref_string = ""
  inside_json = False
  for line in api_ref:
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


gorilla_gql_training_dataset = []
gorilla_gql_dataset = []
for api_ref_path in os.listdir("./APIref"):
  for schema_path in os.listdir("./ToySchemas"):
    api_ref = json_string_from_fopen("./APIref/"+api_ref_path)
    schema = json_string_from_fopen("./ToySchemas/"+schema_path)
    custom_query = generate_query(api_ref, schema)
    print(f"GENERATED QUERY \n {custom_query} \n")
    nlcommand = query_to_command(api_ref, schema, custom_query)
    input = """Your task is to write an API request for a new schema given the API reference and an example.
    The user command is:
    %s
    Here is the API reference for a query that will help with this command and an example of how to use it:
    %s
    Could you please formulate this query for the following schema?
    %s
    VERY IMPORTANT! Please only output the GraphQL for the query and nothing else!
    """ % (nlcommand, api_ref, schema)
    gorilla_gql_training_dataset.append({
      "input": input.replace("\n", ""),
      "output": custom_query.replace("\n", "")
    })
    gorilla_gql_dataset.append({
      "input": input.replace("\n", ""),
      "output": custom_query.replace("\n", ""),
      "api_reference": api_ref_path.replace(".txt", ""),
      "schema": schema_path.replace(".json", "")
    })
    print(f"{len(gorilla_gql_dataset)} \n")
    break
  break

with open('weaviate-gorilla-gql-training-dataset.jsonl', 'w') as f:
    for entry in gorilla_gql_training_dataset:
        json.dump(entry, f)
        f.write('\n')

with open('weaviate-gorilla-gql-dataset.jsonl', 'w') as f:
    for entry in gorilla_gql_dataset:
        json.dump(entry, f)
        f.write('\n')