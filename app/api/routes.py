from . import api_blueprint
from flask import Response, request, jsonify
from app.services import openAI_service, pinecone_service, scrapping_service
from app.utils.utils_functions import *
from openai import OpenAI


PINECONE_INDEX_NAME = "index42"

@api_blueprint.route("/", methods=["POST", "GET", "OPTIONS"])
def home():
    print(f"ENTER: {request.method}")
    return "HELLO - wrong port !"

@api_blueprint.route("/favicon.ico", methods=["POST", "GET", "OPTIONS"])
def favicon():
    return '', 204

@api_blueprint.route("/embed-and-store", methods=["POST", "OPTIONS"])
def embed_and_store():
    if request.method == "OPTIONS":
        return {}, 200  
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


# Build the prompt for the LLM and sending it to the API -> answer.
@api_blueprint.route("/handle-query", methods=["POST", "OPTIONS"])
def handle_query():
    if request.method == "OPTIONS":  # To make flask_cors handle the preflight -> Work on it
        return {}, 200 

@api_blueprint.route("/delete-index", methods=["POST", "OPTIONS"])
def delete_index():
    print("DELETING INDEX endpoint reached")
    pinecone_service.delete_index(PINECONE_INDEX_NAME)
    response_json = {"message": f"Index {PINECONE_INDEX_NAME} deleted successfully"}
    return jsonify(response_json), 200
