import weaviate
import time

def saveData(data, savePath):
   with open(savePath, 'w') as f:
      for entry in data:
         json.dump(entry, f)
         f.write('\n')

f = open("../files/FIQA-Corpus.json")
import json
json_data = json.load(f)
f.close()
json_list = list(json_data)

corpus = []

for json_dict in json_list:
    new_doc_obj = {}
    for key in json_dict.keys():
        # might already have the vector in the file.
        # also have this funny problem of document vs. content as the text key - will be a problem for LLM eval.
        new_doc_obj[key] = json_dict[key]
    corpus.append(new_doc_obj)

failed_uploads = []

print(f"Preparing to upload {len(corpus)} documents to Weaviate.")

from weaviate.util import get_valid_uuid
from uuid import uuid4

client = weaviate.Client("http://localhost:8080")

start = time.time()
for doc in corpus:
    id = get_valid_uuid(uuid4())
    try:
        client.data_object.create(
            data_object = doc,
            class_name = "Document",
            uuid = id
        )
    except:
        print("Failed to upload document.")
        failed_uploads.append(doc)

print(f"Failed to upload {len(failed_uploads)}, saving these to file...")
saveData(failed_uploads, "./failed-uploads.json")


print(f"Uploaded {len(corpus)} documents in {time.time() - start} seconds.")
