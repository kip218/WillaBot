from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
token = os.getenv('token')
challonge_token = os.getenv('challonge_token')
test_token = os.getenv('test_token')
mashape_key = os.getenv('mashape_key')
