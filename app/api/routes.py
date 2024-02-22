from flask import Flask, redirect, url_for, Response, request, jsonify, stream_with_context, json
from app.services import openAI_service, pinecone_service, scrapping_service
from app.utils.utils_functions import *
from . import api_blueprint
import sseclient

# Only one index - no need to get into .env
PINECONE_INDEX_NAME = "index42"


# To scrap the URL, embed the texts, andupload to the vector database.
@api_blueprint.route("/embed-and-store", methods=["POST"])
def embed_and_store():
    # print("Endpoint EMBEDDING reached")
    url = request.json["url"]
    # print(f"URL : {url}")
    url_text = scrapping_service.scrape_website(url)
    chunks = chunk_text(url_text)
    pinecone_service.embed_chunks_and_upload_to_pinecone(chunks, PINECONE_INDEX_NAME)
    response_json = {"message": "Chunks embedded and stored successfully"}
    return jsonify(response_json)


# Get user's question, find relevant context from db,
# Build the prompt for the LLM and sending it to the API -> answer.
@api_blueprint.route("/handle-query", methods=["POST"])
def handle_query():
    question = request.json["question"]
    chat_history = request.json["chatHistory"]
    context_chunks = pinecone_service.get_most_similar_chunks_for_query(
        question, PINECONE_INDEX_NAME
    )
    prompt = build_prompt(question, context_chunks)
    messages = openAI_service.construct_llm_payload(prompt, context_chunks, chat_history)
    
    def generate():
        response = client.completions.create(model=CHATGPT_MODEL,
            prompt=messages,
            temperature=1,
            max_tokens=500,
            n=1,
            stop=None,
            presence_penalty=0,
            frequency_penalty=0.1)
        completion_text = response.choices[0].text
        cleaned_answer = completion_text.strip()
        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.data != '[DONE]':
                try:
                    text = json.loads(event.data)['choices'][0]['delta']['content']
                    yield(text)
                except:
                    yield('')

    # Return the streamed response from the LLM to the frontend
    return Response(stream_with_context(generate()))


# App.js component unmounts calling
# -> to delete this only index we can have and create it again for every new page visit.
@api_blueprint.route("/delete-index", methods=["POST"])
def delete_index():
    pinecone_service.delete_index(PINECONE_INDEX_NAME)
    return jsonify({"message": f"Index {PINECONE_INDEX_NAME} deleted successfully"})
