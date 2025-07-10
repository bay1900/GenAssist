
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
# from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

from agent import query_rewrite, query_hyde, retriever


from src.llm import embedding
from src.utils import yaml, doc_loader

from src.utils.logger import setup_logger
logger = setup_logger(__name__, log_file='logs/file_operations.log')  

async def dense_retrieve( payload_in ): 
    
    provider =  payload_in.provider
    
    payload = {
        "status": False,
        "data": "",
        "msg": ""
    }
    try:
        
        #CONFIG
        config = await yaml.read( "./config/model_config.yaml" )
        if not config["status"]: 
            payload["msg"] = config["msg"]
            return payload
        
        config = config["data"]["dense_retriver_config"][f"{provider}"]
        model_embedding = config["model_embedding"]
        collection = config["collection"]
    
        # GET EMEMBEDDING CLASS
        embeddings = await embedding.embed_class( provider, model_embedding )
        if not embeddings["status"]:
            payload["msg"] = str(embeddings["msg"])
            logger.warning( embeddings["msg"])
            return payload
        embeddings = embeddings["data"]

        # VECTOR
        persist_directory = "./data/vector"
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name=collection
        ) 
        dense_retriever = vector_store.as_retriever( search_type="similarity",
                                                    search_kwargs={'k': 5})
        
        payload["status"] = True
        payload["data"]   = dense_retriever
    except Exception as e:
        payload["msg"] = str(e)
        logger.err( e )

    return payload
    
async def spare_retrieve( payload_in, document ): 
    
    #USER INPUT
    query = payload_in.patient_question #patient
    
    payload = {
        "status": False,
        "data": "",
        "msg": ""
    }
    
    try:
        # CONFIG
        config = await yaml.read( "./config/model_config.yaml" )
        if not config["status"]: 
            payload["msg"] = config["msg"]
            return payload
            
        config = config["data"]["spare_retriver_config"]
        k_result = config["k"]
        
        # LOAD DOCUMENT
        if len( document) == 0 :
            document = await doc_loader.actionplan_document()
            
        # RETRIEVER
        spare_retriever   = BM25Retriever.from_documents ( document )
        spare_retriever.k = k_result
        # spare_result = spare_retriever.invoke( query )
        
        payload["status"] = True
        payload["data"]   = spare_retriever
    except Exception as e: 
        payload["msg"] = str(e)
        logger.error( e )
        
    return payload
    
async def hydbrid_retrieve( dense_retriever, spare_retriever ): 
    payload = {
        "status": False,
        "data": "",
        "msg": ""
    }
    
    try:
        # CONFIG
        config = await yaml.read( "./config/model_config.yaml" )
        if not config["status"]: 
            payload["msg"] = config["msg"]
            return payload
            
        config  = config["data"]["hydbrid_retriever_config"]
        weights = config["weights"]
        hydbrid_retriever = EnsembleRetriever( retrievers = [ dense_retriever, spare_retriever ],
                                               weights    = [ weights["dense"], weights["spare"] ] )      
        
        payload["status"] = True
        payload["data"]   = hydbrid_retriever
    except Exception as e: 
        payload["msg"] = str(e)
        logger.error( e )
    
    return payload

async def retreive_controller(payload_in): 
    
    payload = {
        "status": False,
        "data": "",
        "msg": ""
    }
    
    patient_question = payload_in.patient_question
    
    rewritten = await query_rewrite.query_rewriter(payload_in, provider = "openai" )
    if not rewritten: 
        payload["msg"] = rewritten["msg"]
        logger.warning ( rewritten["msg"] )
        return payload
    rewritten = rewritten["data"]["patient_question_rewritten"]
    
    hyde = await query_hyde.query_hyde( rewritten, provider = "openai" )
    if not rewritten: 
        payload["msg"] = hyde["msg"]
        logger.warning ( hyde["msg"] )
        return payload
    hyde = hyde["data"]["patient_question_hyde"]
    
    spare_retreiver = await retriever.spare_retrieve ( payload_in, "" )
    if not spare_retreiver: 
        payload["msg"] = spare_retreiver["msg"]
        logger.warning ( spare_retreiver["msg"] )
        return payload
    spare_result = spare_retreiver["data"].invoke( patient_question )
    
    dense_retreiver = await retriever.dense_retrieve ( payload_in  )
    if not dense_retreiver: 
        payload["msg"] = dense_retreiver["msg"]
        logger.warning ( dense_retreiver["msg"] )
        return payload
    dense_result = spare_retreiver["data"].invoke( patient_question )
    
    hydbrid_retriever = await retriever.hydbrid_retrieve( dense_retreiver["data"],spare_retreiver["data"] )
    if not hydbrid_retriever: 
        payload["msg"] = hydbrid_retriever["msg"]
        logger.warning ( hydbrid_retriever["msg"] )
        return payload
    hydbrid_result = hydbrid_retriever["data"].invoke( patient_question )
    
    
    return dense_result