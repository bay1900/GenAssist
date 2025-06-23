import re
import uuid

from src.utils import token_counter



async def chunk_actionplan( text ):
    payload = { 
                "status": False,
                "data": "",
                "error": "",
                "topic" : { 
                    "act_plan_count": "",
                    "act_plan_list": [],
                    "distinct_count": "",
                    "distinct_list": []
                },
                "gene" : {
                    "act_plan_count": "",
                    "act_plan_list": [],
                    "distinct_count": "",
                    "distinct_list": []
                }
    }

    async def topic_chuncker(text):
        try:
            topic_arr = []
            display   = [] 
            pattern = r"Topic:\s*(.*?)\n(.*?)(?=\nTopic:|\Z)"

            topic_match = re.findall(pattern, text, re.DOTALL)

            for topic, context in topic_match:

                temp_topic = { 
                    "topic": topic.strip(),
                    "content": context.strip()
                }
                display.append(temp_topic["topic"])
                topic_arr.append(temp_topic)

                distinct_set = set(display)

            payload["topic"]["act_plan_count"] = len(topic_arr)
            payload["topic"]["act_plan_list"]  = display
            payload["topic"]["distinct_count"] = len(distinct_set)
            payload["topic"]["distinct"]       = list(distinct_set)
            print ( len( topic_match ), " topics found")

        except re.error as e:
            payload["error"] = e
            return payload
        except Exception as e: 
            payload["error"] = e
            return payload

        return topic_arr

    async def gene_chunker(): 
        gene_arr = []
        display = []
        topic_chunks = await topic_chuncker(text)
        
        for topic in topic_chunks:
            topic_name = topic["topic"]
            content = topic["content"]
            
            pattern = r"Gene:\s*(.*?)\n(.*?)(?=\nGene:|\Z)"
            gene_match = re.findall(pattern, content, re.DOTALL)
            for gene, gene_content in gene_match:
                if gene in content:
                    temp_topic_gene = {
                        "topic": topic_name,
                        "gene": gene.strip(),
                        "content": gene_content.strip()
                    }
                    display.append(temp_topic_gene["gene"]) 
                    gene_arr.append(temp_topic_gene)
        distinct_set = set(display)
        
        # SUMARY
        payload["gene"]["act_plan_count"] = len(gene_arr)
        payload["gene"]["act_plan_list"] = display
        payload["gene"]["distinct_count"] = len(distinct_set)
        payload["gene"]["distinct_list"] = list(distinct_set)
        print(len(distinct_set), " genes found" )
        return gene_arr

    async def age_chunker():
        age_arr = []
        gene_chunks = await gene_chunker()

        for gene in gene_chunks:
            topic = gene["topic"]
            genes  = gene["gene"]
            content = gene["content"]
            
            pattern = r"Min Age:\s*(\d+)\s*Max Age:\s*(\d+)\s*(.*?)(?=\nMin Age:|\Z)"
            age_match = re.findall(pattern, content, re.DOTALL)
            if age_match:
                for min_age, max_age, age_content in age_match:
                    if min_age in content or max_age in content:
                        temp_topic_age = {
                            "topic": topic,
                            "gene": genes,
                            "min_age": min_age.strip(),
                            "max_age": max_age.strip(),
                            "content": age_content.strip()
                        }
                    age_arr.append(temp_topic_age)
            
        return age_arr

    async def heading_chunker():
        heading_arr = []
        age_chunks = await age_chunker()
        
        
        for age in age_chunks:
            age_name = age["topic"]
            gene     = age["gene"]
            min_age  = age["min_age"]
            max_age  = age["max_age"]
            content  = age["content"]
            
            pattern = r"Heading:\s*(.*?)\n(.*?)(?=\nHeading:|\Z)"

            heading_match = re.findall(pattern, content, re.DOTALL)
            
            for heading, heading_content in heading_match:
    
                if heading in content:
                    temp_topic_heading = {
                        "id": str( uuid.uuid4() ),
                        "topic": age_name,
                        "gene": gene,
                        "min_age": min_age,
                        "max_age": max_age,
                        "token": await token_counter.num_tokens_from_string(heading_content.strip()),
                        "heading": heading.strip(),
                        "content": heading_content.strip()
                    }
                    heading_arr.append(temp_topic_heading)
        
        return heading_arr

    rs = await heading_chunker()
    return rs