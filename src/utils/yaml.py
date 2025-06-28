import yaml

def read ( path ): 
    with open( path, 'r') as file:
        data = yaml.safe_load( file )
        print ( data["openai"] )
        
        return data