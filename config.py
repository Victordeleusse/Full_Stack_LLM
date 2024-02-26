from os import environ, path
from dotenv import load_dotenv

# Determine the path to the .env file
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
