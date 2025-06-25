import re
import uuid

from src.utils import token_counter



async def chunk_actionplan( text ):
    payload = { 
                "status": False,
                "data": "",
                "error": "",
                "topic" : "",
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
            
            topic_summary = { 
                             "act_plan_count" :len(topic_arr),
                             "act_plan_list"  : display,
                             "distinct_count" :len(distinct_set),
                             "distinct"       : list(distinct_set)
                            }
            payload["status"] = True
            payload["data"]   = topic_arr
            payload["topic"]  = topic_summary
            print ( len( topic_match ), " topics found")
            
        except re.error as e:
            payload["status"] = False
            payload["error"] = e
            return payload
        except Exception as e: 
            payload["status"] = False
            payload["error"] = e
        except ValueError as e:
            payload["status"] = False
            payload["error"] = e

        return payload

    async def gene_chunker():

        topic_chunks = await topic_chuncker(text)
        status = topic_chunks["status"]
        
        if not status:
            return topic_chunks
        else:
            gene_arr = []
            display  = []
            try:
                for topic in topic_chunks["data"]:
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
                
                gene_sumary = { 
                            "act_plan_count" : len(gene_arr),
                            "act_plan_list"  : display,
                            "distinct_count" : len(distinct_set),
                            "distinct_list"  : list(distinct_set)
                            }
                
                # SUMARY
                payload["data"] = gene_arr
                payload["gene"] = gene_sumary
                print(len(distinct_set), " genes found" )
                
            except re.error as e:
                payload["status"] = False
                payload["error"] = e
                return payload
            except Exception as e: 
                payload["status"] = False
                payload["error"] = e
            except ValueError as e:
                payload["status"] = False
                payload["error"] = e
            
            return payload

    async def age_chunker():
        gene_chunks = await gene_chunker()
        status = gene_chunks["status"]
        
        if not status:
            return gene_chunks
        else:
            try: 
                age_arr = []
                for gene in gene_chunks["data"]:
                            topic   = gene["topic"]
                            genes   = gene["gene"]
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
                            
                            payload["status"] = True
                            payload["data"] = age_arr
                
            except re.error as e:
                payload["status"] = False
                payload["error"] = e
                return payload
            except Exception as e: 
                payload["status"] = False
                payload["error"] = e
            except ValueError as e:
                payload["status"] = False
                payload["error"] = e
            
        return payload
        
    async def heading_chunker():
        
        age_chunks = await age_chunker()
        status = age_chunks["status"]
        if not status:
            return age_chunks
        else:
            try: 
                heading_arr = []
                for age in age_chunks["data"]:
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
                            
                            payload["status"] = True
                            payload["data"] = heading_arr
            except re.error as e:
                payload["status"] = False
                payload["error"] = e
                return payload
            except Exception as e: 
                payload["status"] = False
                payload["error"] = e
            except ValueError as e:
                payload["status"] = False
                payload["error"] = e
                  
        return payload

    rs = await heading_chunker()
    return rs