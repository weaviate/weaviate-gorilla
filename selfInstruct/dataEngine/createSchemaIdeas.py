import openai
import time
import os

'''

Currently manually scaling this with copy and paste to GPT-4 GUI.

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
'''

# Read Schemas

promptTemplate = """
Your task is to come up with synthetic use cases for a Database.
We currently have the following schemas:\n
"""

for idx, schema in enumerate(os.listdir("../data/ToySchemas")):
    if ".DS_Store" not in schema:
        promptTemplate += f"Schema {idx}: {schema}\n"

for jdx, schema in enumerate(os.listdir("../data/NewSchemas")):
    if ".DS_Store" not in schema:
        promptTemplate += f"Schema {idx+jdx}: {schema}\n"
# For schema in schemas

promptTemplate += """
Can you please propose 20 new schemas?
"""

print(promptTemplate)