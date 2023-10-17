from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json

app = FastAPI()

# Initialize CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount templates directory
templates = Jinja2Templates(directory="templates")

dataPath = "../validatorEngine/failed-WeaviateGorillaGQLDataset.json"

def loadDataFromJSON(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def saveData(data, savePath):
   with open(savePath, 'w') as f:
      for entry in data:
         json.dump(entry, f)
         f.write('\n')

# Load paragraphs from file
paragraphs = loadDataFromJSON(dataPath)

# Define route to serve HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Define route to serve paragraphs as JSON
@app.get("/paragraphs", response_class=JSONResponse)
async def read_paragraphs():
    data = loadDataFromJSON(dataPath)
    #print(row["output"] for row in data)
    return [row["output"] for row in data]

class Paragraph(BaseModel):
    paragraph: str

# Define route to save edited paragraph to file
@app.put("/paragraphs/{index}")
def update_paragraph(index: int, paragraph: Paragraph):
    # Load the existing dataå
    data = loadDataFromJSON(dataPath)

    # Update only the 'output' key
    data[index]['output'] = paragraph.paragraph

    # Write the updated data to file
    saveData(data, "./data/DataForFiltering-619.json")
    
    # Return the updated paragraph or an empty dict if it was deleted
    return paragraph.paragraph

@app.put("/newentry/{index}")
def add_paragraph(paragraph, index: int):
    # If the content is a placeholder, insert a new paragraph with an empty string content at the specified index
    new_paragraph = {"content": "placeholder"}
    paragraphs.insert(index, new_paragraph)

    # Write the updated paragraphs to file
    saveData(paragraphs, "./data/DataForFiltering-619.json")

    return {"message": "Paragraph added successfully."}
