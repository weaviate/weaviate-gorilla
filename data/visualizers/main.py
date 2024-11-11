# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_html():
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HTML file not found")

@app.get("/api/schemas")
async def get_schemas():
    try:
        with open("static/simple-3-collection-schemas.json", "r") as f:
            try:
                data = json.load(f)
                # Assuming the JSON file contains a similar structure with weaviate_collections
                # If it's a direct array of collections, you might not need this next line
                schemas = data.get("weaviate_collections", data)
                return schemas
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Schema file not found")

# Run with: uvicorn main:app --reload