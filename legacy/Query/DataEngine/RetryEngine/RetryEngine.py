import os
import random
import re
from pathlib import Path
import openai
import time
import json
import openai

class RetryEngine:
    def __init__(self, api_key, input_path, output_path):
        self.api_key = api_key
        self.input_path = input_path
        self.output_path = output_path
        openai.api_key = api_key
    
    def Run(self):
        queries = self.loadDataFromJSON(self.input_path)
        data_for_filtering = []
        counter = 0
        start = time.time()
        for example in queries:
            if counter % 50 == 49:
                print(counter)
            api_ref = example["apiRef"]
            schema = example["schema"]
            failed_query = example["output"]
            print(f"FAILED QUERY \n {failed_query}")
            new_query_prompt = self.fixQueryPrompt(api_ref, schema, failed_query)
            new_query = self.openaiRequest(new_query_prompt)
            nlcommand = example["nlcommand"]
            print(f"\n NEW QUERY \n {new_query} \n")

            input_for_training = self.formatInputForGorilla(api_ref, schema, nlcommand)
            data_for_filtering.append({
                "input": input_for_training,
                "output": new_query,
                "nlcommand": nlcommand,
                "apiRef": api_ref,
                "apiRefPath": example["apiRefPath"],
                "schema": schema,
                "schemaPath": example["schemaPath"]
            })
            counter += 1
            if counter % 100 == 99:
                '''
                ToDo, only save the latest 100 each time.
                Add a file to merge the 100s if it crashes.
                Add a CLI argument to offset generation from the crash.
                '''
                print("\n \n \n Save Trigger! \n \n \n")
                print(f"Saving at step... {counter}")
                self.saveData(data_for_filtering, f"{counter}-backup.json")
                print("\n \n File saved! \n \n")
                print(f"Ran for {time.time() - start} seconds so far.")
        
        self.saveData(data_for_filtering, self.output_path)
        print(f"\n \n Created and saved {counter} Weaviate Gorilla queries in {time.time() - start} seconds.")

    def loadDataFromJSON(input_path):
        data = []
        with open(input_path, 'r') as f:
            for line in f:
                data.append(json.loads(line.strip()))
        return data

    def fixQueryPrompt(api_ref, schema, failed_query):
        return 0
    
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
    
    def formatInputForGorilla(api_ref, schema, nlcommand):
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
        """ % (api_ref, schema, nlcommand)
        return inputForGorilla
    
    def saveData(data, save_path):
        with open(save_path, 'w') as f:
            for entry in data:
                json.dump(entry, f)
                f.write('\n')