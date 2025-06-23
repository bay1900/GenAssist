import os

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from fastapi.security import APIKeyHeader

from retriever import fetch_file

load_dotenv()



app = FastAPI(
    title="genAssist Endpoints",
    description="",
    version="1.0.0",
)

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # List of origins that are allowed to make requests
    allow_credentials=True,         # Allow cookies to be included in cross-origin requests
    allow_methods=["*"],            # Allow all standard HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],            # Allow all headers in the request
)

# API Key validation
api_key_header = APIKeyHeader(name="x-api-key", auto_error=True)
async def validate_api_key(api_key: str = Depends(api_key_header)):

    if api_key != "123":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials - Invalid API Key",
            headers={"WWW-Authenticate": "API-Key"},
        )
    return api_key

@app.get("/test_app", dependencies=[Depends(validate_api_key)])
def test_app():
    """
    Test endpoint to check if the application is running.
    """
    return {"message": "genAssist is running successfully!"}    

@app.get("/retrive", dependencies=[Depends(validate_api_key)])
def retrive():
    
    path = './data/actionplan - whole.txt'
    status = fetch_file( path )
    return status