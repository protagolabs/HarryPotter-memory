from elasticsearch import Elasticsearch, helpers
import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import copy
import re
from memoryPrompt import Social_Memory_Template, Combine_Social_Template, Valid_JSON_Template
import json
import time

# 连接到Elasticsearch
es = Elasticsearch("http://localhost:9200")

# 创建social memory索引
def create_social_memory_index(index_name):
    settings = {
        "mappings": {
            "properties": {
                "name": {"type": "text"},
                "other-names": {"type": "text"},
                "description": {"type": "text"},
                "impression": {"type": "text"},
                "relationship": {"type": "text"},
            }
        }
    }
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=settings)

# 创建knowledge memory索引
def create_knowledge_memory_index(index_name):
    settings = {
        "mappings": {
            "properties": {
                "name": {"type": "text"},
                "description": {"type": "text"},
                "learning_context": {"type": "text"},
                "knowledge_content": {"type": "text"},
                "outcome": {"type": "text"}
            }
        }
    }
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=settings)

# 创建interaction memory索引
def create_interaction_memory_index(index_name):
    settings = {
        "mappings": {
            "properties": {
                "name": {"type": "text"},
                "event_id": {"type": "text"},
                "description": {"type": "text"},
                "impression": {"type": "text"},
                "interaction": {"type": "text"},
            }
        }
    }
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=settings)

# 搜索memory，支持多个字段
def search_existing_memory(index_name, query, fields, min_score=1.0, size=1):
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": fields,
                "fuzziness": "AUTO"  # 自动模糊匹配
            }
        },
        "min_score": min_score,  # 仅返回 _score 大于等于 min_score 的结果
        "size": size  # 只返回一个匹配结果
    }
    response = es.search(index=index_name, body=search_body)
    return response["hits"]["hits"]

# 从Elasticsearch中提取所有数据
def fetch_all_documents(index_name, es):
    query = {
        "query": {
            "match_all": {}
        }
    }
    result = es.search(index=index_name, body=query, scroll='2m')  # 设置scroll保留时间为2分钟
    hits = result['hits']['hits']

    scroll_id = result['_scroll_id']
    total_hits = result['hits']['total']['value']

    # 使用scroll API提取所有文档
    while len(hits) < total_hits:
        result = es.scroll(scroll_id=scroll_id, scroll='2m')
        hits += result['hits']['hits']
        scroll_id = result['_scroll_id']
    
    # 提取_source数据
    documents = [hit["_source"] for hit in hits]
    return documents

def run_openai(messages, client):
    
    # Send the prompt to OpenAI's GPT-4
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stop=None,
        temperature=0.7
    )

    answer = response.choices[0].message.content
    
    return answer

def generate_templates(Prompt_Template, input_text):
    """
    Generates template with substituted texts.
    
    """

    # Deep copy the original template to avoid modifying it
    updated_template = copy.deepcopy(Prompt_Template)
        
    # Substitute the placeholder in the user document
    for entry in updated_template:
        if entry["role"] == "user":
            entry["content"] = entry["content"].format(input_text=input_text)
    
    return updated_template

def generate_templates_combine(Prompt_Template, old_card, new_card):
    """
    Generates template with substituted texts.
    
    """

    # Deep copy the original template to avoid modifying it
    updated_template = copy.deepcopy(Prompt_Template)
        
    # Substitute the placeholder in the user document
    for entry in updated_template:
        if entry["role"] == "user":
            entry["content"] = entry["content"].format(old_card=old_card, new_card=new_card)
    
    return updated_template

def extract_social_memory(input_text, client):
    """
    Extracts social memory from the given input text.
    
    """

    # Generate Social Memory using your templates and OpenAI
    Social_Memory = generate_templates(Social_Memory_Template, input_text)
    memory_dict = run_openai(Social_Memory, client)

    # Strip the markdown delimiters (the ```json part)
    cleaned_memory_dict = memory_dict.strip('```json').strip()
    try:
        cleaned_memory_dict = json.loads(cleaned_memory_dict)
    except:
        Json_Template = generate_templates(Valid_JSON_Template, memory_dict)
        memory_dict = run_openai(Json_Template, client)
        cleaned_memory_dict = memory_dict.strip('```json').strip()
        cleaned_memory_dict = json.loads(cleaned_memory_dict)
    
    return cleaned_memory_dict

def update_social_profile(old_card,new_card):
    Combine_Memory = generate_templates_combine(Combine_Social_Template, old_card, new_card)
    combine_memory_dict = run_openai(Combine_Memory, client)
    # Strip the markdown delimiters (the ```json part)
    cleaned_combine_memory_dict = combine_memory_dict.strip('```json').strip()
    try:
        # convert string to dictionary
        updated_profile = json.loads(cleaned_combine_memory_dict)
    except:
        Json_Template = generate_templates(Valid_JSON_Template, combine_memory_dict)
        combine_memory_dict = run_openai(Json_Template, client)
        cleaned_combine_memory_dict = combine_memory_dict.strip('```json').strip()
        updated_profile = json.loads(cleaned_combine_memory_dict)
    
    return updated_profile


if __name__ == "__main__":
    # Load the environment variables from the .env file
    load_dotenv()

    # Initialize OpenAI client
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)

    # 创建索引,先读取已有的数据
    social_memory_index = "social_memory"
    knowledge_memory_index = "knowledge_memory"
    interaction_memory_index = "interaction_memory"
    create_social_memory_index(social_memory_index)
    create_knowledge_memory_index(knowledge_memory_index)
    create_interaction_memory_index(interaction_memory_index)

    # Helper function to load JSONL and return list of documents
    def load_jsonl(filepath):
        documents = []
        with open(filepath, 'r') as file:
            for line in file:
                documents.append(json.loads(line.strip()))
        return documents

    # Load data from JSONL files
    social_memory_docs = load_jsonl('social_memory.jsonl')
    knowledge_memory_docs = load_jsonl('knowledge_memory.jsonl')
    interaction_memory_docs = load_jsonl('interaction_memory.jsonl')

    # Function to bulk insert into Elasticsearch
    def bulk_insert(index_name, docs):
        actions = [
            {
                "_index": index_name,
                "_source": doc
            }
            for doc in docs
        ]
        helpers.bulk(es, actions)

    # Insert the data into Elasticsearch
    bulk_insert(social_memory_index, social_memory_docs)
    bulk_insert(knowledge_memory_index, knowledge_memory_docs)
    bulk_insert(interaction_memory_index, interaction_memory_docs)

    print("Data has been successfully inserted into Elasticsearch.")


    # Process each line (each chapter) in the JSONL file
    count = 0
    filepath = '/Users/elricwan/Downloads/NetmindAI/HarryPotter-memory/episodic_memory/episodic_events.jsonl'
    with open(filepath, 'r') as infile:
        for line in infile:
            count += 1
            if count <= 100:
                continue
            event_data = json.loads(line.strip())  # Load the chapter (JSON object)
            event_id = list(event_data.keys())[0]  
            # collect social memory for this event
            cleaned_memory_dict = extract_social_memory(event_data, client)

            current_social_memory = cleaned_memory_dict['social_memory']
            current_knowledge_memory = cleaned_memory_dict['knowledge_memory']

            for person in current_social_memory:
                social_query = person['name']
                social_fields = ['name', 'other-names']
                social_results = search_existing_memory(social_memory_index, social_query, social_fields)
                # update interaction memory 
                interaction_profile = {
                            "name": social_query,
                            "event_id": event_id,
                            "description": person["description"],
                            "impression": person["impression"],
                            "interaction": person["interaction"],
                        }
                        
                # 保存interaction memory
                es.index(index=interaction_memory_index, body=interaction_profile)

                # 保存social memory
                if not social_results:
                    es.index(index=social_memory_index, body=person)
                else:
                    # 获取现有数据的ID和_source内容
                    existing_doc_id = social_results[0]['_id']
                    existing_profile = social_results[0]['_source']
                    old_card = existing_profile
                    new_card = person
                    
                    updated_profile = update_social_profile(old_card,new_card)
                    try:
                        # 删除旧文档
                        es.delete(index=social_memory_index, id=existing_doc_id)
                    except:
                        time.sleep(1)

                    # 保存更新后的文档
                    for update_pro in updated_profile['merged_profile']:
                        es.index(index=social_memory_index, body=update_pro)
                    
            for knowledge in current_knowledge_memory:
                knowledge_query = knowledge['name']
                knowledge_fields = ['name', 'description',"knowledge_content"]
                knowledge_results = search_existing_memory(knowledge_memory_index, knowledge_query, knowledge_fields)
                if not knowledge_results:
                    es.index(index=knowledge_memory_index, body=knowledge)

    # 提取所有文档
    doc1 = fetch_all_documents(social_memory_index,es)
    doc2 = fetch_all_documents(knowledge_memory_index,es)
    doc3 = fetch_all_documents(interaction_memory_index,es)

    def save_to_jsonl(documents, filename):
        with open(filename, 'w') as f:
            for document in documents:
                f.write(json.dumps(document) + '\n')

    # Sort doc3 by event_id before saving
    if 'event_id' in doc3[0]:
        doc3 = sorted(doc3, key=lambda x: int(re.findall(r'\d+', x['event_id'])[0]))

    # Save the data to JSONL files
    save_to_jsonl(doc1, 'social_memory_complete.jsonl')
    save_to_jsonl(doc2, 'knowledge_memory_complete.jsonl')
    save_to_jsonl(doc3, 'interaction_memory_complete.jsonl')




