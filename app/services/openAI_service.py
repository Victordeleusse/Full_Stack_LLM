import os
import json
import requests
from app.utils.utils_functions import *


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
OPENAI_URL_EMBEDDING = "https://api.openai.com/v1/embeddings"
CHATGPT_MODEL = "gpt-3.5-turbo-instruct"


# Get embeddings for a given chunk given OpenAI. Version v1 ?
# It will be stored in the vector database, along with the chunk's target text.
# Manage Index ?
def get_embedding(chunk):
    url = OPENAI_URL_EMBEDDING
    headers = {
        "content-type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    data = {"model": OPENAI_EMBEDDING_MODEL, "input": chunk}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_json = response.json()
    embedding = response_json["data"][0]["embedding"]
    return embedding


# Need to run openai migration HERE !
def construct_llm_payload(question, context_chunks, chat_history):
    # Build the prompt with the context chunks and user's query
    prompt = build_prompt(question, context_chunks)
    print("\n==== PROMPT ====\n")
    print(prompt)
    # Construct messages array to send to OpenAI
    # messages = construct_messages_list(chat_history, prompt)
    return prompt
