import openai
import json

def openaiRequest(prompt):
    return openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {
        "role": "system",
        "content": "Your task is to evaluate the performance of a search engine."
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

def readJSON(filepath):
    f = open(filepath)
    json_data = json.load(f)
    f.close()
    json_list = list(json_data)
    data = []
    for json_dict in json_list:
        new_obj = {}
        for key in json_dict.keys():
            new_obj[key] = json_dict[key]
        data.append(new_obj)
    return data