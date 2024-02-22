import os
from . import api_blueprint
from flask import Blueprint, Flask, redirect, url_for, Response, request, jsonify, stream_with_context, json, make_response
from app.services import openAI_service, pinecone_service, scrapping_service
from app.utils.utils_functions import *
import sseclient
import requests
from flask_cors import CORS

# api_blueprint = Blueprint('api_blueprint', __name__)

# Only one index - no need to get into .env
PINECONE_INDEX_NAME = "index42"

# To scrap the URL, embed the texts, andupload to the vector database.
@api_blueprint.route("/embed-and-store", methods=["POST", "OPTIONS"])
def embed_and_store():
    if request.method == "OPTIONS":  # Let flask_cors handle the preflight
        return {}, 200  # A simple 200 OK, or let flask_cors handle it automatically

    print("ENDPOINT embed-and-store reached")
    print("Headers:", request.headers)
    print("Data:", request.data)
    try:
        url = request.json.get("url")
        print(f"URL : {url}")
        if not url:
            return jsonify({"message": "URL is required"}), 400
        url_text = scrapping_service.scrape_website(url)
        chunks = chunk_text(url_text)
        pinecone_service.embed_chunks_and_upload_to_pinecone(chunks, PINECONE_INDEX_NAME)
        response_json = {"message": "Chunks embedded and stored successfully"}
        return jsonify(response_json), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


# Get user's question, find relevant context from db,
# Build the prompt for the LLM and sending it to the API -> answer.
@api_blueprint.route("/handle-query", methods=["POST", "OPTIONS"])
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
@api_blueprint.route("/delete-index", methods=["POST", "OPTIONS"])
def delete_index():
    print("DELETING INDEX endpoint reached")
    pinecone_service.delete_index(PINECONE_INDEX_NAME)
    response_json = {"message": f"Index {PINECONE_INDEX_NAME} deleted successfully"}
    return jsonify(response_json), 200
