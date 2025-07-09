
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from src.llm import embedding
from src.utils import yaml, doc_loader

from src.utils.logger import setup_logger
logger = setup_logger(__name__, log_file='logs/file_operations.log')  

async def dense_retrieve( query, payload_in ): 
    
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
        vector_store_verify = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name=collection
        ) 
        retrieved_docs = vector_store_verify.similarity_search(query, k=2)
        payload["status"] = True
        payload["data"]   = retrieved_docs
    except Exception as e:
        payload["msg"] = str(e)
        logger.err( e )

    return payload
    
async def spare_retrieve( payload_in ): 
    
    #USER INPUT
    query = payload_in.patient_question #patient
    
    payload = {
        "status": False,
        "data": "",
        "msg": ""
    }
    
    try:
        # CONFIG
        config = await yaml.read( "./config/model_confi.yaml" )
        if not config["status"]: 
            payload["msg"] = config["msg"]
            return payload
            
        config = config["data"]["spare_retriver_config"]
        k_result = config["k"]
        
        # LOAD DOCUMENT
        document = await doc_loader.actionplan_document()
        
        # RETRIEVER
        spare_retriever   = BM25Retriever.from_documents ( document )
        spare_retriever.k = k_result
        spare_result = spare_retriever.get_relevant_documents( query )
        
        payload["status"] = True
        payload["data"]   = spare_result
    except Exception as e: 
        payload["msg"] = str(e)
        logger.error( e )
        
    return payload
    
async def hydbrid_retrieve ( query, payload_in ): 
    
    # DENSE
    dense_result = dense_retrieve (query, payload_in )
    
    # SPARE
    spare_result = spare_result   ( query, document )
    hydbrid_retrieve = EnsembleRetriever ( 
                                          retrievers= [ 
                                                        lambda q: dense_result,
                                                        lambda q: spare_result
                                                      ],
                                          weights=[0.6, 0.4] #
                                         )
    
    hydbrid_result = hydbrid_retrieve.get_relevant_documents( query )
    
    return hydbrid_result