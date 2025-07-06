from langchain_core.prompts import PromptTemplate

from src.utils import helper
from src.llm.chat_model import get_chat_model
import uuid
from src.utils.logger import setup_logger, request_id_var
logger = setup_logger(__name__, log_file='logs/file_model.log')  

async def query_rewriter( payload_input, provider="openai"):
    
    req_id = str(uuid.uuid4())
    request_id_var.set(req_id)
    
    user              = payload_input.user
    patient_question  = payload_input.patient_question
    
    payload = {
                "status": False,
                "data": "",
                "msg": "",
                "req_id": req_id
              }
    try: 
        llm = await get_chat_model( provider )
        if not llm["status"]:  
            payload["msg"] = llm["msg"]         
            return payload
        
        llm_model  = llm["data"]["model"]
        llm_prompt = llm["data"]["prompt"]
        prompt_tempalte = PromptTemplate.from_template(llm_prompt)
        chain  = prompt_tempalte | llm_model
        result  = chain.invoke({ 
                                # "output_language": "English",
                                "patient_question": f"{patient_question}"
                              })
        data = { 
                "patient_question": f"{patient_question}",
                "patient_question_rewritten" : result.content,
                "usage" : result.usage_metadata
                }
         
        payload["status"] = True
        payload["data"]   = data
        
        user_chat_hist_path = f"./data/chat_hist/{user}.json"
        await helper.save_chat( user_chat_hist_path, data )
    except Exception as e: 
        payload["msg"] = e
        logger.error( e)
        
    return payload

