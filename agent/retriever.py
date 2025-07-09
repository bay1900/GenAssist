
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document

from src.llm import embedding
from src.utils import yaml

from src.utils.logger import setup_logger
logger = setup_logger(__name__, log_file='logs/file_operations.log')  

async def dense_retrieve( payload_in, query ): 
    
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
    
    # Ensure embeddings are defined (e.g., from OpenAI)
    
    
    
    # embeddings = OpenAIEmbeddings()

    # # Define your documents
    # documents = [
    #     Document(page_content="The quick brown fox jumps over the lazy dog.", metadata={"source": "lorem_ipsum"}),
    #     Document(page_content="Artificial intelligence is transforming industries.", metadata={"source": "tech_news"}),
    #     Document(page_content="ChromaDB is a vector database.", metadata={"source": "documentation"}),
    # ]

    # persist_directory = "../data/vector"

    # # 1. Initialize Chroma and ADD documents (if this is the first run or you want to re-add)
    # #    Use .from_documents() to create and add documents at once, and persist.
    # vector_store = Chroma.from_documents(
    #     documents=documents,
    #     embedding=embeddings,
    #     persist_directory=persist_directory
    # )
    # # Important: Call persist() explicitly if you are not using .from_documents directly
    # # or in certain environments (like Jupyter notebooks)
    # # vector_store.persist()
    # print(f"Documents added and persisted to: {persist_directory}")

    # # 2. Later, when you want to load and query:
    # #    Make sure you are loading from the SAME persist_directory
    # loaded_vector_store = Chroma(
    #     persist_directory=persist_directory,
    #     embedding_function=embeddings,
    # )

    # query = "What is a vector database?"
    # results = loaded_vector_store.similarity_search(query, k=2)

    # if results:
    #     print("\nRetrieved results:")
    #     for doc in results:
    #         print(f"- Content: {doc.page_content[:50]}...")
    #         print(f"  Metadata: {doc.metadata}")
    # else:
    #     print("\nNo results found. This might mean the data wasn't persisted or loaded correctly.")
