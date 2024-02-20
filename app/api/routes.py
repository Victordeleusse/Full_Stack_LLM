from flask import Flask, redirect, url_for, request, jsonify
from app.services import openAI_service, pinecone_service, scrapping_service
from app.utils.utils_functions import *
from . import api_blueprint
# app = Flask(__name__)

# Only one index - no need to get into .env
PINECONE_INDEX_NAME = 'index42'

# To scrap the URL, embed the texts, andupload to the vector database.
@api_blueprint.route('/embed-and-store', methods=['POST'])
def embed_and_store():
    print("Endpoint EMBEDDING reached")
    url = request.json['url']
    print(f"URL : {url}")
    url_text = scrapping_service.scrape_website(url)
    chunks = chunk_text(url_text)
    pinecone_service.embed_chunks_and_upload_to_pinecone(chunks, PINECONE_INDEX_NAME)
    response_json = { "message": "Chunks embedded and stored successfully" }
    return jsonify(response_json)

# Get user's question, find relevant context from db,
# Build the prompt for the LLM and sending it to the API -> answer.
@api_blueprint.route('/handle-query', methods=['POST'])
def handle_query():
    question = request.json['question']
    context_chunks = pinecone_service.get_most_similar_chunks_for_query(question, PINECONE_INDEX_NAME)
    prompt = build_prompt(question, context_chunks)
    answer = openAI_service.get_llm_answer(prompt)
    return jsonify({ "question": question, "answer": answer })    
