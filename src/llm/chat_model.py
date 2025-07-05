from langchain_mistralai.chat_models import ChatMistralAI
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic 

from src.utils import yaml, env, helper

from src.utils.logger import setup_logger
logger = setup_logger(__name__, log_file='logs/file_operations.log')    

MODEL_MAPPING = {
    "mistral" : ChatMistralAI,
    "deepseek": ChatDeepSeek,
    "openai" : ChatOpenAI, 
    "gemini"  : ChatGoogleGenerativeAI,
    "claude"  : ChatAnthropic
}

async def get_chat_model(model: str, 
                         provider: str = "openai"):
    
    payload = {
                "status": False,
                "data": "",
                "error": "", 
                "msg": ""
              }
    try: 
        model = model.lower() 
        selected_chat_model = MODEL_MAPPING.get( provider )
        
        if not selected_chat_model:
                logger.error(f"Unsupported model: {model}. Available models: {list(MODEL_MAPPING.keys())}")
                payload["error"] = f"Unsupported model: {model}. Available models: {list(MODEL_MAPPING.keys())}"
                return payload
                
        KEY    = await helper.get_key( provider )
        
        config = await yaml.read( "./config/model_config.yaml" )
        config = config["data"]["rewritter_model"][f"{provider}"]
        
        
        chat_model = selected_chat_model(
                        api_key = KEY,
                        model   = config["model"],
                        temperature = config["temperature"],
                        max_tokens  = config["max_tokens"]
        )
        
        payload["status"] = True
        payload["data"]   = chat_model
        
    except Exception as e: 
            payload["error"] = e
            logger.error(e )
    
    return payload