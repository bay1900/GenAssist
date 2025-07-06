from langchain_core.prompts import PromptTemplate
from agent import query_hyde
from src.utils import helper
from src.llm.chat_model import get_chat_model
import uuid
from src.utils.logger import setup_logger, request_id_var
logger = setup_logger(__name__, log_file='logs/file_model.log')  

async def query_rewriter( payload_input, provider="openai"):
    
    # model_config.yaml
    root_key = "rewritter_model" 
    
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
        llm = await get_chat_model( provider, root_key )
        if not llm["status"]:  
            payload["msg"] = llm["msg"]         
            return payload
        
        llm_model  = llm["data"]["model"]
        llm_prompt = llm["data"]["prompt"]
        prompt_tempalte = PromptTemplate.from_template(llm_prompt)
        chain  = prompt_tempalte | llm_model
        rewrite_result  = chain.invoke({ 
                                # "output_language": "English",
                                "patient_question": f"{patient_question}"
                              })
        patient_question_rewritten = rewrite_result.content
        patient_question_rewritten_usage = rewrite_result.usage_metadata
        
        patient_question_hyde = await query_hyde.query_hyde( patient_question_rewritten, provider = "openai" )
        if not patient_question_hyde["status"]:
            logger.warning( patient_question_hyde["msg"] )
        patient_question_hyde_content = patient_question_hyde['data'].content
        patient_question_hyde_usage   = patient_question_hyde['data'].usage_metadata
        
        usage = { 
                 "rewritten": patient_question_rewritten_usage,
                 "hyde": patient_question_hyde_usage
                }
        
        data = { 
                "patient_question": f"{patient_question}",
                "patient_question_rewritten" : patient_question_rewritten,
                "patient_question_hyde" : patient_question_hyde_content,
                "usage" : usage
                }
         
        payload["status"] = True
        payload["data"]   = data
        
        user_chat_hist_path = f"./data/chat_hist/{user}.json"
        await helper.save_chat( user_chat_hist_path, data )
    except Exception as e: 
        payload["msg"] = e
        logger.error( e)
        
    return payload

