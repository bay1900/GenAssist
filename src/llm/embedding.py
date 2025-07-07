import os 
import json
from pathlib import Path
from langchain_community.document_loaders import JSONLoader

import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_mistralai import MistralAIEmbeddings

from src.utils import yaml, env, helper

from src.utils.logger import setup_logger

logger = setup_logger(__name__, log_file='logs/file_operations.log')    

async def embed_class( embedding_provider, embedding_model ): 

    payload = {
                "status": False,
                "data": "",
                "error": "", 
                "msg": ""
              }
    EMBED_MAPPING = { 
        "openai"   : OpenAIEmbeddings,
        "mistral"  : MistralAIEmbeddings
    }
    
    # CHECK PROVIDER
    embedding_map = EMBED_MAPPING.get( embedding_provider )
    if embedding_map is None:
        payload["error"] = f"Unsupport Embedding Provider {embedding_provider}"
        logger.error( f"Unsupport Embedding Provider ``{embedding_provider}``" )
        return payload
    
    # CHECK IF PROVIDER SUPPORT
    path = await env.read( "MODEL_CONFIG")
    if not path["status"]:
        payload["msg"] = path["status"]
        logger.warning( path["status"] )
    path = path["data"]
    
    data = await yaml.read( path )
    if not data["status"]:
        payload["msg"] = data["status"]
        logger.warning( data["status"] )
    data = data["data"]
    
    embedding_model_list = data["embedding_model_list"][f"{embedding_provider}"]
    # print ( "embedding_model_list : ", embedding_model_list )
    
    # CHECK IF MODEL OF PROVIDER SUPPORT
    if embedding_model not in embedding_model_list:
        payload["error"] = f"Unsupport Embedding Model {embedding_model} for Provider {embedding_provider}"
        logger.error( f"Unsupport Embedding Model ``{embedding_model}`` - Provider ``{embedding_provider}``" )
        return payload
    
    KEY = await helper.get_key( embedding_provider )
    if not KEY["status"]:
        payload["msg"] = KEY["status"]
        logger.warning( KEY["status"] )
    KEY = KEY["data"]
    
    # GET EMBEDDING CLASS
    embedding_class = classmethod
    if embedding_provider == "openai":
        embedding_class = OpenAIEmbeddings( api_key = KEY, model=embedding_model)
    elif embedding_provider == "mistral":
        embedding_class = MistralAIEmbeddings( mistra_api_key = KEY,model=embedding_model )
        
    payload["status"] = True
    payload["data"] = embedding_class
    
    return payload
     
def embed( llm ):  
     
    payload = {  
                "status": False,
                "data": "",
                "error": "", 
                "msg": ""
              }  
      
    # PATH
    config_path = env.read( "MODEL_CONFIG")
    
    # PROPERTY 
    property    = yaml.read( config_path )
    llm_propery = ""
    try:
        llm_propery = property["data"][llm]
    except KeyError as e : 
        err = f"Unsupport Model {e}",
        payload["error"] = err
        
        logger.error( err )
        return payload
            
    # VALUE
    api    = llm_propery["api"]
    vector = llm_propery["vector"]
    model_chat  = llm_propery["model_chat"]
    
    
    embed = embed_model( llm, api )
    
    
    
    print ( "embed : ", embed )
    return payload