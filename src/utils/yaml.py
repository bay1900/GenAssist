import yaml
import os

from src.utils.logger import setup_logger

logger = setup_logger(__name__, log_file='logs/file_operations.log')    

async def read ( file_path ): 
    with open( file_path, 'r') as file:
        data = yaml.safe_load( file )

    payload = { 
           "status": False,
           "data": "",
           "msg": ""}
    try:
        # Check if the file exists and is not empty before attempting to read
        if not os.path.exists(file_path):
            payload["msg"] = f"File not found: {file_path}"
            logger.warning(f"Error: File not found: {file_path}")
            return payload
        
        if os.path.getsize(file_path) == 0:
            payload["msg"] = f"File is empty: {file_path}"
            logger.warning(f"File is empty: {file_path}")
            return payload
        
        with open( file_path, 'r') as file:
            data = yaml.safe_load( file )
            
            payload["status"] = True
            payload["data"]   = data
            
            logger.info(f"File read successfully: {file_path}")
            return payload

    except FileNotFoundError:
        payload["msg"] = f"File not found: {file_path}"
        logger.warning(f"Error: File not found: {file_path}")
        return  payload
        

    except UnicodeDecodeError:
        payload["error"] = (f"Error: Could not decode file: {file_path}. Check encoding.")
        logger.warning(f"Error: Could not decode file: {file_path}. Check encoding.")
        return  payload

    except Exception as e:
        payload["error"] = (f"Unexpected error while reading {file_path}: {e}")
        logger.error(f"Unexpected error while reading {file_path}: {e}")
        return  payload