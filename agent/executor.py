
from src.llm.chat_model import get_chat_model
from src.utils import yaml, doc_loader

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.prompts import PromptTemplate
from src.llm import embedding

from langchain_chroma import Chroma
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import Tool
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from langchain import hub



async def agent_executor():
    
    root_key = "agent_executor_config"
    
    payload = {
        "status": False,
        "data": "",
        "msg": ""
    }
    
    # CONFIG
    config = await yaml.read( "./config/model_config.yaml" )
    if not config["status"]: 
        payload["msg"] = config["msg"]
        return payload
    
    config   = config["data"][root_key]
    provider = config["provider"]
    provider_property = config[provider]
    sys_prompt   = config["sys_prompt"] # "MaterPrompt not ProviderPrompt"
    tool_desc_action_plan    = config["tool_desc_action_plan"]
    vector_k     = config["vector_k"]
  
    # GET EMEMBEDDING CLASS
    model_embedding = provider_property["model_embedding"]
    embedding_func = await embedding.embed_class( provider, model_embedding )
    if not embedding_func["status"]:  
        payload["msg"] = embedding_func["msg"]         
        return payload
    embedding_func = embedding_func["data"]
    
    # VECTOR STORE
    vectordb = Chroma( 
            persist_directory  = "../data/vector/6509ba0f-d540-4f55-b16c-2486b1266306",
            embedding_function = embedding_func
    )
    
    retriever = vectordb.as_retriever(search_type="similarity", 
                                      search_kwargs={"k": vector_k })
    
    # CHAT MODEL
    chat_model = await get_chat_model( provider, root_key )
    if not chat_model["status"]:  
        payload["msg"] = chat_model["msg"]         
        return payload
    chat_model = chat_model["data"]["model"]
    
    # --------- MESSAGE ---------
    # SYSTEM
    system_prompt = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=["context"],
            template= sys_prompt,
        )
    )
    # HUMAN
    human_prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=["question"],
            template="{question}",
        )
    )
    # COMBINE MESSAGES
    messages = [system_prompt, human_prompt]
    
    # --------- PROMPT ---------
    prompt_template = ChatPromptTemplate(
        input_variables=["context", "question", "chat_history"],
        messages=messages
    )
    
    agent_prompt = hub.pull("hwchase17/react-chat") # LangSmithMissingAPIKeyWarning
    
    vector_chain = (
            {
              "context": retriever, 
              "question":  RunnablePassthrough(),
              "chat_history": RunnablePassthrough()
            } 
            | prompt_template
            | chat_model
            | StrOutputParser()
    )
    
    # --------- TOOL ---------
    actionplan_tool = Tool(
            name  = "ActionPlan",
            func  = vector_chain.invoke,
            description = tool_desc_action_plan,
        )
    tools = [ actionplan_tool ]
    
    
    # --------- EXECUTOR ---------
    agent = create_react_agent( llm    = chat_model, 
                                tools  = tools, 
                                prompt = agent_prompt )
    
    agent_executor = AgentExecutor(
        agent = agent,
        tools= tools,
        verbose= True,
        handle_parsing_errors= True,
        return_intermediate_steps= True
    )
    
    result = agent_executor.invoke( {"input": "I am a man with BRCA1 and have not had screening, is there any imaging I should be doing?", 
                                     "chat_history": [],       
                                    #  "intermediate_steps": []  
                                     })

    return result