import chromadb
from langchain_openai import OpenAIEmbeddings

from src.utils import yaml, env


def embed( llm = "openai"):    
    config_path = env.read( "MODEL_CONFIG")
    
    # PROPERTY 
    property = yaml.read( config_path )
    
    
    print ( " property : ", property )