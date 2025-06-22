
def read(file_path):
    
    payload = { 
           "status": False,
           "data": "",
           "error": ""}
    try:
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