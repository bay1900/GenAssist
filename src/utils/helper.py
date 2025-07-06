import os
import json

from src.utils import yaml, env, file

from src.utils.logger import setup_logger
logger = setup_logger(__name__, log_file='logs/file_operations.log')  


async def get_key ( provider): 
    payload = {
                "status": False,
                "data": "",
                "msg": ""
              }
    
    try:
        config = await yaml.read( "./config/model_config.yaml" )
        if not config["status"]: 
            payload["msg"] = config["msg"]
            return payload 
    
        env_key = config["data"][f"{provider}"]["key"]
        key = await env.read( env_key ) 
        
        payload["status"] = True
        payload["data"]   = key["data"]
        
    except Exception as e: 
        payload["msg"] = e
        logger.error( e )
    
    return payload


async def save_chat(user_chat_hist_path, data_to_write): 
    
    payload = { 
        "status": False,
        "data": "",
        "error": "",
        "msg": ""
    }

    previous_chat = []
    merge_chat    = []
    exist = os.path.exists(user_chat_hist_path)
    if exist:
        try:
            with open(user_chat_hist_path, "r", encoding="utf-8") as f:
                loaded_data   = json.load(f)
                previous_chat.append(loaded_data)
                
                previous_chat.append( data_to_write) # append new chat
                
            with open(user_chat_hist_path, 'w', encoding="utf-8") as f:
                json.dump(previous_chat, f, indent=4)
                
            payload["status"] = True
            # logger.info( "")
        except Exception as e:
            payload["error"]  = e
            logger.error( e )
    else: 
        try: 
            await file.write_json ( user_chat_hist_path, data_to_write )
            payload["status"] = True
        except Exception as e: 
            payload["error"]  = e
            logger.error( e )
    return payload
 
