from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
token = os.getenv('token')
challonge_token = os.getenv('challonge_token')
DATABASE_URL = os.getenv('DATABASE_URL')
