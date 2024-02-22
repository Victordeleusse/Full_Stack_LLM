import os
from flask import Flask
from flask_cors import CORS
from app.api.routes import api_blueprint

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    app.register_blueprint(api_blueprint)
    return app