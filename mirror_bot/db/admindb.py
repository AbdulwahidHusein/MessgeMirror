import os
from dotenv import load_dotenv
from pymongo import MongoClient
from config import Config



client = MongoClient(Config.MONGO_URL)
db = client['MirrorBot']
admins_collection = db['adminlist']

def add_username_to_admin_list(username): 
    if not is_admin(username):
        admins_collection.insert_one({'username': username})
        return f"@{username} has been successfully added as an admin."
    else:
        return f"@{username} is already an admin."

def is_admin(username):
    return admins_collection.find_one({'username': username}) is not None

def remove_from_admin_list(username):
    result = admins_collection.delete_one({'username': username})
    if result.deleted_count > 0:
        return True
    return False

def load_admin_list():
    return [doc['username'] for doc in admins_collection.find()]

