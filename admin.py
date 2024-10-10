import json
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
load_dotenv()

# Generate a key for encryption (save this securely for decryption)
# Run this only once to generate and store the key securely.
# key = Fernet.generate_key()
# with open("secret.key", "wb") as key_file:
#     key_file.write(key)

def load_key():
    return os.getenv("ENCRYPTION_KEY")

key = load_key()

cipher_suite = Fernet(key)

# Encrypted file path
adminlist = "adminlist.enc"

# Function to encrypt data and save it to the file
def saveto_admin_list(user_list):
    json_data = json.dumps(user_list).encode('utf-8')
    encrypted_data = cipher_suite.encrypt(json_data)
    with open(adminlist, "wb") as f:
        f.write(encrypted_data)

# Function to load and decrypt the user list from the file
def load_admin_list():
    if not os.path.exists(adminlist):
        return []
    
    with open(adminlist, "rb") as f:
        encrypted_data = f.read()
    
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode('utf-8'))
    except Exception as e:
        print(f"Error decrypting user list: {e}")
        return []

# Function to check if a username exists
def is_admin(username):
    user_list = load_admin_list()
    return username in user_list

# Function to add a username to the list if it doesn't exist
def add_username(username):
    user_list = load_admin_list()
    if username not in user_list:
        user_list.append(username)
        saveto_admin_list(user_list)
        print(f"Username '{username}' added.")
    else:
        print(f"Username '{username}' already exists.")

# Usage example
if __name__ == "__main__":
    # Add a new user
    add_username("cl168888_pg")

    # Check if a user exists
    if is_admin("use41"):
        print("User exists")
    else:
        print("User does not exist")
        
    print(load_admin_list())
