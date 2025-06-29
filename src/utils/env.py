import os 

def read ( key ):
    data = os.getenv( key )
    return str( data )