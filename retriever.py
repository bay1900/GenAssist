
import re
import uuid
import tiktoken

from src.utils import file
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
    
async def knowledge_base():
    
    path = './data/actionplan - whole.txt'
    data = await file.read( path )
    status = data["status"]
    if not status: return data 
    
    chunks = await chunker.chunk_actionplan ( data["data"] )
    
    
    