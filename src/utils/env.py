import os 
from dotenv import load_dotenv


async def read ( key ):
    load_dotenv()
    data = os.getenv( key )
    return str( data )