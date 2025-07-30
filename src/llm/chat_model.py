from langchain_mistralai.chat_models import ChatMistralAI
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic 

from src.utils import yaml, env, helper

from src.utils.logger import setup_logger
logger = setup_logger(__name__, log_file='logs/file_operations.log')    

PROVIDER_MAPPING = {
    "mistral" : ChatMistralAI,
    "deepseek": ChatDeepSeek,
    "openai"  : ChatOpenAI, 
    "gemini"  : ChatGoogleGenerativeAI,
    "claude"  : ChatAnthropic
}

async def get_chat_model( provider: str, root_key: str ):
 
    
    payload = {
                "status": False,
                "data": "",
                "msg": ""
              }
    try: 
        provider = provider.lower() 
        
        # MODEL MAPPING
        selected_chat_model = PROVIDER_MAPPING.get( provider )
        if not selected_chat_model:
                logger.error(f"Unsupported model: {provider}. Available models: {list(PROVIDER_MAPPING.keys())}")
                payload["msg"] = f"Unsupported model: {provider}. Available models: {list(PROVIDER_MAPPING.keys())}"
                return payload
        
        # GET API KEY
        KEY    = await helper.get_key( provider ) 
        if not KEY["status"]: 
                payload["msg"] = KEY["msg"]
                logger.warning( KEY["msg"] )
                return payload
        KEY    = KEY["data"]
        
        # CONFIG rewritter_model
        config = await yaml.read( "./config/model_config.yaml" )
        if not config["status"]: 
            payload["msg"] = config["msg"]
            logger.warning( config["msg"] )
            return payload 
        config = config["data"][root_key][f"{provider}"]
        
        # MODEL CLIENT
        chat_model = selected_chat_model(
                        api_key = KEY,
                        model   = config["model"],
                        temperature = config["temperature"],
                        max_tokens  = config["max_tokens"]
        )
        
        # PROMPT
        prompt = config["prompt"]
        
        # TEMP DATA
        temp_data = { 
                     "model": chat_model,
                     "prompt": prompt or ""
                    }
         
        payload["status"] = True
        payload["data"]   = temp_data
    except KeyError as e: 
            payload["msg"] = str( f'Key error: { e }') 
            logger.warning(e )
    except Exception as e: 
            payload["msg"] = str(e) 
            logger.error(e )
    
    return payload