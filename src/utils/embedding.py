import os 
import json
from pathlib import Path
from langchain_community.document_loaders import JSONLoader

import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_mistralai import MistralAIEmbeddings

from src.utils import yaml, env

from src.utils.logger import setup_logger

logger = setup_logger(__name__, log_file='logs/file_operations.log')    

def embed_model ( llm, api): 

    os.environ[api]
    EMBED_MAPPING = { 
        "openai"   : OpenAIEmbeddings,
        "mistral"  : MistralAIEmbeddings
    }
    
    model = classmethod
    try: 
        model = EMBED_MAPPING.get( llm )
        if model is None: 
            raise ValueError
    except ValueError as e: 
        err = f"Unsupport Embeding Model {llm}"
        logger.error( err ) 
    except KeyError as e: 
        err = f"Unsupport Embeding Model {llm}"
        logger.error( err ) 
           
    return model 
    
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