
from langchain_chroma.vectorstores import Chroma
from src.llm import embedding
from src.utils.logger import setup_logger

from src.utils import yaml, env, vector


import chromadb

logger = setup_logger(__name__, log_file='logs/log_vector.log')  

async def get_or_create_vector( collection_name: str, 
                                embedding_model: classmethod, 
                                persist_directory: str, 
                                documents: list):
    payload = {
        "status": False,
        "data": None,
        "error": "",
        "msg": ""
    }

    try:
        
        client = chromadb.PersistentClient(path=persist_directory)
        exist = False 
        try:
            collection_exist = client.get_collection(name=collection_name)
            exist = True
        except Exception as e: 
            pass
            
        
        if exist:
            # Collection already exists, load it and add documents
            logger.info(f"Collection '{collection_name}' already exists in '{persist_directory}'")
            payload["msg"] = f"Collection '{collection_name}' already existed"

            # LangChain's Chroma wrapper to load the existing collection
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embedding_model,
                collection_name=collection_name
            )
            # Add the new documents to the existing collection
            # vector_store.add_documents(documents)
        else:
            # Collection does not exist, create it from documents
            logger.info(f"Collection '{collection_name}' does not exist in '{persist_directory}'. Creating a new one.")
            payload["msg"] = f"New collection '{collection_name}' created. Documents added."

            persistent_client = chromadb.PersistentClient()
            collection = persistent_client.get_or_create_collection(collection_name)
            
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=embedding_model,
                persist_directory=persist_directory,
                collection_name=collection_name
            ) 

            payload["status"] = True
            # payload["data"] = vector_store # Store the vector_store object
            
            
    except Exception as e:
        logger.error(f"Error in get_or_create_vector: {e}", exc_info=True) # exc_info for traceback
        payload["error"] = str(e)
        payload["msg"] = f"Failed to create/update vector store for collection '{collection_name}' due to an error."
    
    
    
    return payload


async def get_collection( persist_directory: str):
        payload = {
            "status": False,
            "data": None,
            "error": "",
            "msg": ""
        }
        
        try:
            
            client = chromadb.PersistentClient(path=persist_directory)
            collection = client.list_collections()
            logger.info(f"Retrieved collections from '{persist_directory}': {collection}")
            payload["status"] = True
            payload["data"] = collection    
            payload["msg"] = f"Successfully retrieved collections from '{persist_directory}'"
            
            
        except Exception as e:
            logger.error(f"Error in get_collection: {e}", exc_info=True) # exc_info for traceback
            payload["error"] = str(e)
            payload["msg"] = f"Failed to retrieve collections from '{persist_directory}' due to an error."
            
        return payload
    
async def chroma_controller( func_code ): 
    
    payload = {
        "status": False,
        "data": None,
        "error": "",
        "msg": ""
    }
    
    # GET COLLECTIONS
    if func_code == "01": 
        path = await env.read( "FILE_PATH_CONFIG")
        data = await yaml.read( path)
        
        persist_directory = data["data"]["actionplan"]["actionplan_vector_path"]
        collections = await vector.get_collection( persist_directory )
        collections = collections["data"]

        arr = []
        for col in collections:
            arr.append( {
                "name": col.name})
        
        payload["status"] = True
        payload["data"] = arr
    else:
        payload["error"] = f"Unsupported function code: {func_code}"
        logger.error(payload["error"])
        
        
    return payload