import os

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from src.llm import embedding
from model import param
from src.utils import yaml, env, vector
from agent import query_rewrite, retriever
from dotenv import load_dotenv
from retriever import knowledge_base

from pydantic import BaseModel, ValidationError


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
    print ( data        )
    return data   

@app.get("/embedding_model_list", dependencies=[Depends(validate_api_key)])
async def embedding_model_list():
    
    path = await env.read( "MODEL_CONFIG")
    data = await yaml.read( path)
    embedding_model_list = data["data"]["embedding_model_list"]
    return embedding_model_list 

@app.post("/chroma", dependencies=[Depends(validate_api_key)])
async def chroma_func( payload: param.Chroma_input):
    
    func_code = payload.func_code
    
    result = await vector.chroma_controller( func_code )
    
    return result


@app.post("/embed_knowledgebase", dependencies=[Depends(validate_api_key)])
async def retrive( payload: param.Embed_knowledgebase_input):
    
    # PAYLOAD
    is_embedding       = payload.is_embedding
    embedding_provider = payload.embedding_provider
    embedding_model    = payload.embedding_model
    
    # EMBEDDING CLASS
    # check if embedding provider and model are supported
    embedding_class = await embedding.embed_class( embedding_provider, embedding_model )
    if embedding_class["status"] == False: return embedding_class # RETURN IF ERROR
    embedding_class = embedding_class["data"] #overwrite embedding_class with the actual class
    
    status = await knowledge_base(is_embedding, embedding_provider, embedding_model, embedding_class )
    return status   

@app.post("/chat", dependencies=[Depends(validate_api_key)])
async def chat_gen( payload: param.Chat_input):
    
    # rewritten = await query_rewrite.query_rewriter(payload, provider = "openai" )
    dense_result = await retriever.dense_retrieve ( payload, "what is BRCA1?",  )
    return dense_result