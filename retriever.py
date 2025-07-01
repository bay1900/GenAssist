
import re
import uuid
import tiktoken

from src.utils import file, embedding, env, yaml
from src.chunk import chunker



async def fetch_file(path):
    data = await file.read( path )

    # # chunks = await chunker.chunk_actionplan ( data["data"] )
    
    # # print ( "chunks : ", chunks)
    
    # return data
    
    
    status = data["status"]
    if status:
        return data["data"] 
    else:
        return data
    
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
     
    # if is_embedding:  
    #     embedding.embed()
    #     print ( "embed function here " )
    # else: 
    #     chunks = await chunker.chunk_actionplan ( data["data"] )
    
    return "chunks"
    