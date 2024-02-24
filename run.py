import os
from app import create_app
from dotenv import load_dotenv

load_dotenv()

app, socketio = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)