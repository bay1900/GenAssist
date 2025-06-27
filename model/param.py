from pydantic import BaseModel, PydanticUserError, ValidationError

class Embed_knowledgebase_input( BaseModel ): 

    
  
        embedding: bool
    
    
    # except PydanticUserError as e:
        
    #     print( e )