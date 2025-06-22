from src.utils import file


def fetch_file(path):
    data = file.read( path )
    
    status = data["status"]
    if status:
        return data["data"] 
    else:
        return data
    
    