
from langchain_chroma.vectorstores import Chroma
from src.utils.logger import setup_logger

import chromadb

logger = setup_logger(__name__, log_file='logs/log_vector.log')  

async def get_or_create_vector( collection_name: str, embedding_model: classmethod, persist_directory: str, llm: str, documents: list):
    payload = {
        "status": False,
        "data": None, # Initialize data to None
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
            logger.info(f"Collection '{collection_name}' already exists in '{persist_directory}'. Loading it and adding new documents.")
            payload["msg"] = f"Collection '{collection_name}' already existed. Documents added."

            # LangChain's Chroma wrapper to load the existing collection
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embedding_model,
                collection_name=collection_name
            )
            # Add the new documents to the existing collection
            vector_store.add_documents(documents)
        else:
            # Collection does not exist, create it from documents
            logger.info(f"Collection '{collection_name}' does not exist in '{persist_directory}'. Creating a new one.")
            payload["msg"] = f"New collection '{collection_name}' created. Documents added."

            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=embedding_model,
                persist_directory=persist_directory,
                collection_name=collection_name
            )

        payload["status"] = True
        payload["data"] = vector_store # Store the vector_store object

            
    except Exception as e:
        logger.error(f"Error in get_or_create_vector: {e}", exc_info=True) # exc_info for traceback
        payload["error"] = str(e)
        payload["msg"] = f"Failed to create/update vector store for collection '{collection_name}' due to an error."
