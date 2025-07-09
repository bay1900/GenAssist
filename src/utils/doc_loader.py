from langchain_community.document_loaders import JSONLoader
from src.utils import yaml

async def actionplan_document():
    def metadata_func(record: dict, metadata: dict) -> dict:
        """
        Function to extract additional metadata from each JSON record.
        """
        metadata["id"] = record.get("id")
        metadata["topic"] = record.get("topic")
        metadata["gene"] = record.get("gene")
        metadata["min_age"] = record.get("min_age")
        metadata["max_age"] = record.get("max_age") 
        metadata["heading"] = record.get("heading")
        return metadata
    
    # CONFIG
    config = await yaml.read( "./config/file_path_config.yaml" )
    if not config["status"]: return config
    
    # CONFIG ACTIONPLAN
    actionplan_config = config["data"]["actionplan"]
    actionpan_json_path = actionplan_config["actionplan_json_path"]
    
    # LOAD JSON FILE
    loader = JSONLoader(
        file_path= actionpan_json_path,
        jq_schema=".[]",             # Select each object in the array
        content_key="content",       # Use 'content' as the main content
        metadata_func=metadata_func  # Apply the custom metadata function
    )
    
    # Load the documents from the JSON file
    # This will return a list of Document objects with the specified content and metadata.
    document = loader.load() 
    
    return document