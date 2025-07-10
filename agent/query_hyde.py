from langchain_core.prompts import PromptTemplate

from src.utils import helper
from src.llm.chat_model import get_chat_model
import uuid
from src.utils.logger import setup_logger, request_id_var
logger = setup_logger(__name__, log_file='logs/file_model.log')  

async def query_hyde( query, provider="openai"):
    
    # model_config.yaml
    root_key = "HyDE_config" 
    
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
        hyde_result  = chain.invoke({ 
                                "patient_question": f"{query}"
                              })
        patient_question_hyde = hyde_result.content
        model_name = hyde_result.response_metadata["model_name"]
        
        usage = { 
            "usage_metadata": { 
                "input_tokens": hyde_result.usage_metadata["input_tokens"],
                "output_tokens": hyde_result.usage_metadata["output_tokens"]
            },
            "token_usage": { 
                "completion_tokens": hyde_result.response_metadata["token_usage"]["completion_tokens"],
                "prompt_tokens": hyde_result.response_metadata["token_usage"]["prompt_tokens"]
            }
        }
        
        data = { 
                "patient_question_hyde" : patient_question_hyde,
                "usage" : usage,
                "model_name": model_name
                }
        
        payload["status"] = True
        payload["data"]   = data
        

    except Exception as e: 
        payload["msg"] = e
        logger.error( e)
        
    return payload

