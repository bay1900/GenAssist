import os

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from model import param
from src.utils import yaml
from dotenv import load_dotenv
from retriever import knowledge_base

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    list_of_ints: list[int]
    a_float: float


data = dict(
    list_of_ints=['1', 2, 'bad'],
    a_float='not a float',
)

try:
    Model(**data)
except ValidationError as e:
    print(e)
    """
    2 validation errors for Model
    list_of_ints.2
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='bad', input_type=str]
    a_float
      Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='not a float', input_type=str]
    """

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

@app.get("/model_config", dependencies=[Depends(validate_api_key)])
def model_config():
    
    data = yaml.read ( "./config/model_config.yaml")
    
    return data   

@app.post("/embed_knowledgebase", dependencies=[Depends(validate_api_key)])
async def retrive( payload: param.Embed_knowledgebase_input):
    
    is_embedding = payload.is_embedding
    
    status = await knowledge_base(is_embedding)
    return status