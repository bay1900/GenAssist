from src.utils import yaml, env


async def get_key ( provider): 
    # CHECK IF PROVIDER SUPPORT
    path = await env.read( "MODEL_CONFIG")
    data = await yaml.read( path )
    env_key = data["data"][f"{provider}"]["key"]
    key = await env.read( env_key ) 
    
    return key