from pydantic import BaseModel

class Embed_knowledgebase_input( BaseModel ): 
  
        is_embedding: bool
        embedding_provider: str
        embedding_model: str
        
class Chroma_input( BaseModel ):
  
        # persist_directory: str
        func_code: str
