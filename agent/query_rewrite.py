from langchain_core.prompts import PromptTemplate

from src.utils import helper
from src.llm.chat_model import get_chat_model

from src.utils.logger import setup_logger
logger = setup_logger(__name__, log_file='logs/file_model.log')  

async def query_rewriter( payload_input, provider="openai"):
    
    user              = payload_input.user
    patient_question  = payload_input.patient_question
    
    payload = {
                "status": False,
                "data": "",
                "error": "", 
                "msg": ""
              }
    try: 
        llm = await get_chat_model( provider)
        llm = llm["data"]
        
        prompt = PromptTemplate.from_template("Rewrite the following query to be more specific:\n{patient_question}")
        chain  = prompt | llm
        
        result  = chain.invoke(
            { 
                # "output_language": "English",
                "patient_question": "are you ai ?",
            }
        )
        data = { 
                "patient_question": "test2",
                "patient_question_rewritten" : result.content,
                "usage" : result.usage_metadata
                }
        
        payload["status"] = True
        payload["data"]   = data
        
        user_chat_hist_path = f"./data/chat_hist/{user}.json"
        await helper.save_chat( user_chat_hist_path, data )
    except Exception as e: 
        payload["error"] = e
        logger.error( e)
    
    return payload

