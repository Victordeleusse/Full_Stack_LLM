from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from app.api.routes import api_blueprint
from flask_socketio import SocketIO, emit

from app.services import openAI_service, pinecone_service, scrapping_service
from app.utils.utils_functions import *
from openai import OpenAI

PINECONE_INDEX_NAME = "index42"
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    app.register_blueprint(api_blueprint)
    socketio.init_app(app) 
    return app

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('send_message')
def handle_message(data):
    # Process the message sent by the client
    print('Received message:', data)
    emit('receive_message', {'text': 'This is a response from the server.'})
    
@socketio.on('send_question')
def handle_question(data):
    question = data['question']
    chat_history = data['chatHistory']
    context_chunks = pinecone_service.get_most_similar_chunks_for_query(question, PINECONE_INDEX_NAME)
    messages = openAI_service.construct_llm_payload(question, context_chunks, chat_history)
    client = OpenAI()
    response = client.completions.create(
        model=CHATGPT_MODEL,
        prompt=messages,
        temperature=1,
        max_tokens=500,
        n=1,
        presence_penalty=0,
        frequency_penalty=0.1,
        stop=["\n", " Human:", " AI:"])
    answer = response.choices[0].text.strip()
    
    emit('new_message', {'text': answer, 'isBot': True})