
import re
import uuid
import tiktoken
import chromadb


from langchain_community.document_loaders import JSONLoader
from langchain_chroma.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from llm import embedding
from src.utils import file, env, yaml, vector, helper
from src.chunk import chunker

  
async def knowledge_base( is_embedding, embedding_provider, embedding_model, embedding_class ):
    
    # CONFIG
    config = await yaml.read( "./config/file_path_config.yaml" )
    if not config["status"]: return config
    
    # CONFIG ACTIONPLAN
    actionplan_config = config["data"]["actionplan"]

    # ACTIONPLAN TEXT READ
    actionplan_text_path = actionplan_config["actionplan_text_path"]
    actionplan_text = await file.read( actionplan_text_path )
    if not actionplan_text["status"]: return actionplan_text 
    
    # CHUNKING TEXT TO JSON
    text = actionplan_text["data"]
    chunks = await chunker.chunk_actionplan ( text )
    if not chunks["status"]: return chunks
    
    # WRITE JSON FILE
    # if json file exists, it will skip creating a new one
    actionpan_json_path = actionplan_config["actionplan_json_path"]
    actionpan_json      = await file.write_json( actionpan_json_path, chunks["data"] )
    if not actionpan_json["status"]: return actionpan_json
    
    # METADATA FUNCTION
    # This function extracts metadata from each JSON record and returns it as a dictionary.
    def metadata_func(record: dict, metadata: dict) -> dict:
        """
        Function to extract additional metadata from each JSON record.
        """
        metadata["id"] = record.get("id")
        metadata["topic"] = record.get("topic")
        metadata["gene"] = record.get("gene")
        metadata["min_age"] = record.get("min_age")
        metadata["max_age"] = record.get("max_age") 
        metadata["heading"] = record.get("heading")
        return metadata
    
    # LOAD JSON FILE
    loader = JSONLoader(
        file_path= actionpan_json_path,
        jq_schema=".[]",             # Select each object in the array
        content_key="content",       # Use 'content' as the main content
        metadata_func=metadata_func  # Apply the custom metadata function
    )
    
    # Load the documents from the JSON file
    # This will return a list of Document objects with the specified content and metadata.
    documents = loader.load() 

    embeddings = embedding_class
    
    # VECTOR
    actionplan_vector_path = actionplan_config["actionplan_vector_path"]
    vector_store = await vector.get_or_create_vector(
            collection_name= f"{embedding_provider}_{embedding_model}_collection",
            embedding_model=embeddings,
            persist_directory=actionplan_vector_path,
            documents=documents
    )
    return vector_store
    