import os
from flask import Blueprint, Flask
from flask_cors import CORS
from app import create_app
from app.api.routes import api_blueprint
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)