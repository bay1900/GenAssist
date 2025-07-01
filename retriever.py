
import re
import uuid
import tiktoken

from langchain_community.document_loaders import JSONLoader

from src.utils import file, embedding, env, yaml
from src.chunk import chunker

    
async def knowledge_base( is_embedding, llm ):
    
    # CONFIG
    config = await yaml.read( "./config/file_path_config.yaml" )
    actionplan_config = config["data"]["actionplan"]
    
    # ACTIONPLAN TEXT READ
    actionplan_text_path = actionplan_config["actionplan_text_path"]
    data = await file.read( actionplan_text_path )
    status = data["status"]
    if not status: return data 
    
    # CHUNKING TEXT TO JSON
    chunks = await chunker.chunk_actionplan ( data["data"] )
    
    # WRITE JSON FILE
    actionpan_json_path = actionplan_config["actionplan_json_path"]
    await file.write_json( actionpan_json_path, chunks["data"] )
    
    # VECTOR
    actionplan_vector_path = actionplan_config["actionplan_vector_path"]
    
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

    loader = JSONLoader(
        file_path= actionpan_json_path,
        jq_schema=".[]", # Select each object in the array
        content_key="content", # Use 'review_text' as the main content
        metadata_func=metadata_func # Apply the custom metadata function
    )
    
    documents = loader.load()   
    
    
    return "chunks"
    