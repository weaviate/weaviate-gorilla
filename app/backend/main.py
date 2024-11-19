# uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import json
import os

with open("llama3.1:8b-experiment_results-with-models.json", 'r') as f:
    sample_data = json.load(f)

# Access detailed_results array instead of trying to index the root object
print(sample_data["detailed_results"][0])

@app.get("/data")
async def get_data():
    return sample_data