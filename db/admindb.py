import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client['admin_database']
collection = db['adminlist']

def add_username_to_admin_list(username):
    if not is_admin(username):
        collection.insert_one({'username': username})
        return f"Username '{username}' added."
    else:
        return f"Username '{username}' already exists."

def is_admin(username):
    return collection.find_one({'username': username}) is not None

def load_admin_list():
    return [doc['username'] for doc in collection.find()]

