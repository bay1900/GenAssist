import os 
from dotenv import load_dotenv

from src.utils.logger import setup_logger
logger = setup_logger(__name__, log_file='logs/file_operations.log') 
  
async def read ( key ):
    payload = { 
                "status": False,
                "data": "",
                "msg": ""
              }
    try:
        load_dotenv() # LOAD ENV VARIABLE
        data = os.getenv(key)

        if data is not None:
            payload["status"] = True
            payload["data"]   = str(data)
        else:
            payload["msg"] = f"Warning: Environment variable '{key}' not found." 
            logger.warning(f"Warning: Environment variable '{key}' not found." )
    except Exception as e:
        payload["msg"] = f"An error occurred while reading environment variable '{key}': {e}"

    return payload