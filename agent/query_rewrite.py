from langchain_core.prompts import PromptTemplate
from agent import query_hyde
from src.utils import helper
from src.llm.chat_model import get_chat_model
import uuid
from src.utils.logger import setup_logger, request_id_var
logger = setup_logger(__name__, log_file='logs/file_model.log')  

async def query_rewriter( payload_input, provider="openai"):
    
    # model_config.yaml
    root_key = "rewritter_config" 
    
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
                                "patient_question": f"{patient_question}"
                              })
        patient_question_rewritten = rewrite_result.content
        model_name = rewrite_result.response_metadata["model_name"]
        
        usage = { 
            "usage_metadata": { 
                "input_tokens": rewrite_result.usage_metadata["input_tokens"],
                "output_tokens": rewrite_result.usage_metadata["output_tokens"]
            },
            "token_usage": { 
                "completion_tokens": rewrite_result.response_metadata["token_usage"]["completion_tokens"],
                "prompt_tokens": rewrite_result.response_metadata["token_usage"]["prompt_tokens"]
            }
        }
        
        data = { 
                "patient_question": f"{patient_question}",
                "patient_question_rewritten" : patient_question_rewritten,
                "usage" : usage,
                "model_name": model_name
                }
         
        payload["status"] = True
        payload["data"]   = data
        
        user_chat_hist_path = f"./data/chat_hist/{user}.json"
        await helper.save_chat( user_chat_hist_path, data )
    except Exception as e: 
        payload["msg"] = e
        logger.error( e)
        
    return payload

