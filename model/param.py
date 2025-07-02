from pydantic import BaseModel

class Embed_knowledgebase_input( BaseModel ): 
  
        is_embedding: bool
        embedding_provider: str
        embedding_model: str