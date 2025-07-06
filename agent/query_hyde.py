from langchain_core.prompts import PromptTemplate

from src.utils import helper
from src.llm.chat_model import get_chat_model
import uuid
from src.utils.logger import setup_logger, request_id_var
logger = setup_logger(__name__, log_file='logs/file_model.log')  

async def query_hyde( query, provider="openai"):
    
    # model_config.yaml
    root_key = "hyde_model" 
    
    req_id = str(uuid.uuid4())
    request_id_var.set(req_id)
    
    payload = {
                "status": False,
                "data": "",
                "msg": "",
                "req_id": req_id
              }
    try: 
        llm = await get_chat_model( provider, root_key )
        if not llm["status"]:  
            payload["msg"] = llm["msg"]         
            return payload
        
        llm_model  = llm["data"]["model"]
        llm_prompt = llm["data"]["prompt"]
        prompt_tempalte = PromptTemplate.from_template(llm_prompt)
        chain   = prompt_tempalte | llm_model
        result  = chain.invoke({ 
                                # "output_language": "English",
                                "patient_question": f"{query}"
                              })

         
        payload["status"] = True
        payload["data"]   = result
        

    except Exception as e: 
        payload["msg"] = e
        logger.error( e)
        
    return payload

