import os
import json

async def read(file_path):
    
    payload = { 
           "status": False,
           "data": "",
           "error": ""}
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
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
            
            payload["status"] = True
            payload["data"]   = data
            
            print(f"File read successfully: {file_path}")
            return payload

    except FileNotFoundError:
        payload["error"] = f"File not found: {file_path}"
        print(f"Error: File not found: {file_path}")
        return  payload
        

    except UnicodeDecodeError:
        payload["error"] = (f"Error: Could not decode file: {file_path}. Check encoding.")
        print(f"Error: Could not decode file: {file_path}. Check encoding.")
        return  payload

    except Exception as e:
        payload["error"] = (f"Unexpected error while reading {file_path}: {e}")
        print(f"Unexpected error while reading {file_path}: {e}")
        return  payload
    
async def read_json(file_path):
    
    payload = { 
           "status": False,
           "data": "",
           "error": ""}
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
            
            print(f"File read successfully: {file_path}")
            return payload

    except FileNotFoundError:
        payload["error"] = f"File not found: {file_path}"
        print(f"Error: File not found: {file_path}")
        return  payload

    except UnicodeDecodeError:
        payload["error"] = (f"Error: Could not decode file: {file_path}. Check encoding.")
        print(f"Error: Could not decode file: {file_path}. Check encoding.")
        return  payload

    except Exception as e:
        payload["error"] = (f"Error while reading {file_path}: {e}")
        print(f"Error while reading {file_path}: {e}")
        return  payload
    
async def write_json(file_path, data_to_write):
    
    payload = { 
           "status": False,
           "data": "",
           "error": ""}
    try:
        # file_exist = os.path.exists(file_path)
        # file_size  = os.path.getsize(file_path) == 0
        
        # WRITE WHEN IF FILE IS NOT EXIST OR EMPTY
        # This prevents overwriting existing data unless the file is empty
        # if not file_exist or file_size:
        
        with open(file_path, 'w') as file:
            json.dump(data_to_write, file, indent=4)

            payload["status"] = True
            payload["data"]   = data_to_write

            print(f"File write successfully: {file_path}")
            return payload

    except Exception as e:
        payload["error"] = (f"Error while writing {file_path}: {e}")
        print(f"Error while writing {file_path}: {e}")
        return  payload