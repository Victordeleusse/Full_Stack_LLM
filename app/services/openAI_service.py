import os
import json
import requests
from openai import OpenAI

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_EMBEDDING_MODEL = 'text-embedding-ada-002'
OPENAI_URL_EMBEDDING = 'https://api.openai.com/v1/embeddings'
CHATGPT_MODEL = 'text-davinci-003'


# Get embeddings for a given chunk given OpenAI. Version v1 ?
# It will be stored in the vector database, along with the chunk's target text.
# Manage Index ?

def get_embedding(chunk):
    url = OPENAI_URL_EMBEDDING
    headers = {
        'content-type': 'application/json; charset=utf-8',
        'Authorization': f"Bearer {OPENAI_API_KEY}"            
    }
    data = {
        'model': OPENAI_EMBEDDING_MODEL,
        'input': chunk
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))  
    response_json = response.json()
    print(f"RESPONSE JSON : {response_json}")
    embedding = response_json["data"][0]["embedding"]
    return embedding

def get_llm_answer(prompt):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.append({"role": "user", "content": prompt})
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'content-type': 'application/json; charset=utf-8',
        'Authorization': f"Bearer {OPENAI_API_KEY}"            
    }
    data = {
        'model': CHATGPT_MODEL,
        'messages': messages,
        'temperature': 1, 
        'max_tokens': 1000
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    # return the final answer
    response_json = response.json()
    completion = response_json["choices"][0]["message"]["content"]
    return completion