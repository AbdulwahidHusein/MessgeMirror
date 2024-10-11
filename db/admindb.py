import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URI)
db = client['admin_database']
admins_collection = db['adminlist']

def add_username_to_admin_list(username):
    if not is_admin(username):
        admins_collection.insert_one({'username': username})
        return f"Username '{username}' added."
    else:
        return f"Username '{username}' already exists."

def is_admin(username):
    return admins_collection.find_one({'username': username}) is not None

def remove_from_admin_list(username):
    result = admins_collection.delete_one({'username': username})
    if result.deleted_count > 0:
        return True
    return False

def load_admin_list():
    return [doc['username'] for doc in admins_collection.find()]

