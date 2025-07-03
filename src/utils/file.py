import os
import json

from src.utils.logger import setup_logger

logger = setup_logger(__name__, log_file='logs/file_operations.log')    

async def read(file_path):
    
    payload = { 
           "status": False,
           "data": "",
           "error": ""}
    try:
        # Check if the file exists and is not empty before attempting to read
        if not os.path.exists(file_path):
            payload["error"] = f"File not found: {file_path}"
            logger.info(f"Error: File not found: {file_path}")
            return payload
        
        if os.path.getsize(file_path) == 0:
            payload["error"] = f"File is empty: {file_path}"
            logger.info(f"File is empty: {file_path}")
            return payload
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
            
            payload["status"] = True
            payload["data"]   = data
            payload["msg"]    = f"File read successfully: {file_path}"
            
            logger.info(f"File read successfully: {file_path}")
            return payload

    except FileNotFoundError:
        payload["error"] = f"File not found: {file_path}"
        logger.error(f"Error: File not found: {file_path}")
        return  payload
        

    except UnicodeDecodeError:
        payload["error"] = (f"Error: Could not decode file: {file_path}. Check encoding.")
        logger.error(f"Error: Could not decode file: {file_path}. Check encoding.")
        return  payload

    except Exception as e:
        payload["error"] = (f"Unexpected error while reading {file_path}: {e}")
        logger.error(f"Unexpected error while reading {file_path}: {e}")
        return  payload
    
async def read_json(file_path):
    
    payload = { 
        "status": False,
        "data": "",
        "error": "",
        "msg": ""
    }
    try:
        # Check if the file exists and is not empty before attempting to read
        if not os.path.exists(file_path):
            payload["error"] = f"File not found: {file_path}"
            print(f"Error: File not found: {file_path}")
            return payload
        
        if os.path.getsize(file_path) == 0:
            payload["error"] = f"File is empty: {file_path}"
            print(f"File is empty: {file_path}")
            return payload
        
        with open(file_path, 'r') as file:
            data = json.load(file) 
            
            payload["status"] = True
            payload["data"]   = data
            payload["msg"]    = f"File read successfully: {file_path}"
            
            logger.info(f"File read successfully: {file_path}")
            return payload

    except FileNotFoundError:
        payload["error"] = f"File not found: {file_path}"
        logger.error(f"Error: File not found: {file_path}")
        return  payload

    except UnicodeDecodeError:
        payload["error"] = (f"Error: Could not decode file: {file_path}. Check encoding.")
        logger.error(f"Error: Could not decode file: {file_path}. Check encoding.")
        return  payload

    except Exception as e:
        payload["error"] = (f"Error while reading {file_path}: {e}")
        logger.error(f"Error while reading {file_path}: {e}")
        return  payload
    
async def write_json(file_path, data_to_write):
    
    payload = { 
                "status": False,
                "data": "",
                "error": "",
                "msg": ""
             }

    # WRITE WHEN IF FILE IS NOT EXIST OR EMPTY
    # This prevents overwriting existing data unless the file is empty
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        try:
                with open(file_path, 'w') as file:
                    json.dump(data_to_write, file, indent=4)

                payload["status"] = True
                payload["data"]   = data_to_write

                logger.info(f"File write successfully: {file_path}")
                return payload

        except Exception as e:
            payload["error"] = (f"Error while writing {file_path}: {e}")
            logger.error(f"Error ss while writing {file_path}: {e}")
            return  payload 
    else:
        payload["status"] = True
        payload["msg"] = f"File already exists and is not empty: {file_path}. Skipping write operation."
        logger.warning(f"File already exists and is not empty: {file_path}. Skipping write operation.")
    
    return payload
