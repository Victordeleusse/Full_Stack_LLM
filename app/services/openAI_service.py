import os
import json
import requests
from openai import OpenAI

client = OpenAI()
from openai import OpenAI
import time

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_EMBEDDING_MODEL = 'text-embedding-ada-002'
OPENAI_URL_EMBEDDING = 'https://api.openai.com/v1/embeddings'
CHATGPT_MODEL = 'gpt-3.5-turbo-instruct'


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
    embedding = response_json["data"][0]["embedding"]
    return embedding

# Need to run openai migration HERE !
def get_llm_answer(prompt):
    response = client.completions.create(model=CHATGPT_MODEL,
    prompt=prompt,
    temperature=1,
    max_tokens=500,
    n=1,
    stop=None,
    presence_penalty=0,
    frequency_penalty=0.1)   
    completion_text = response.choices[0].text
    print(f"Completion Text: {completion_text}")
    return completion_text