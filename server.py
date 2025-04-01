from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Set
import uvicorn
import json
import os

from standalone_parser import CLRParser

# Custom JSON encoder for handling sets and other non-serializable types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

# Request model
class ParserRequest(BaseModel):
    grammar: List[str] = Field(..., description="List of grammar productions (e.g. ['S->CC', 'C->cC', 'C->d'])")
    input_string: str = Field(..., description="Input string to be parsed")

app = FastAPI(
    title="CLR Parser App",
    description="A web application for parsing context-free grammars using CLR(1) parsing technique",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Create a parser instance
parser = CLRParser()

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """Serve the CLR Parser frontend"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
async def api_info():
    """Root endpoint with information about the API"""
    return {
        "message": "Welcome to CLR Parser API",
        "version": "1.0.0",
        "endpoints": {
            "/parse": "Parse a string using the CLR parsing algorithm",
            "/docs": "API documentation"
        }
    }

def convert_sets_to_lists(obj: Any) -> Any:
    """Convert sets to lists recursively in a dictionary or list"""
    if isinstance(obj, dict):
        return {k: convert_sets_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets_to_lists(item) for item in obj]
    elif isinstance(obj, set):
        return [convert_sets_to_lists(item) for item in obj]
    else:
        return obj

@app.post("/parse")
async def parse_input(request: ParserRequest):
    """
    Parse input string using CLR(1) parsing algorithm.
    
    This endpoint accepts:
    - Grammar productions (e.g. S->CC, C->cC, C->d)
    - Input string to be parsed
    
    It returns:
    - First and Follow sets for non-terminals
    - Parsing table
    - Parsing steps
    - Whether the input is accepted by the grammar
    """
    try:
        # Initialize the parser with the grammar
        parser.initialize_parser(request.grammar)
        
        # Parse the input string
        parser.parse_input(request.input_string)
        
        # Get the result
        result = parser.get_result()
        
        # Convert sets to lists for JSON serialization
        serializable_result = convert_sets_to_lists(result)
        
        return JSONResponse(content=serializable_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app_with_frontend:app", host="0.0.0.0", port=port, reload=True) 