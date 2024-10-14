
from pymongo import MongoClient
from config import Config 

# MongoDB Configuration
MONGO_URL = Config.MONGO_URL
client = MongoClient(MONGO_URL)
db = client['settlement_verification']

# Collection references
group_pairs_collection = db['group_pairs']
settlement_requests_collection = db['settlement_requests']
membership_collection = db['memberships']
user_session_collection = db["user_session"]
whitelist_collection = db['whitelist']
