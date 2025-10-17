from supabase import create_client, Client
import hashlib
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from Streamlit secrets
load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL", "https://tzjrpockqmevrcfqxmuw.supabase.co")
key = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR6anJwb2NrcW1ldnJjZnF4bXV3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA1ODE2MjYsImV4cCI6MjA3NjE1NzYyNn0.QFUjG7-JW_w9DoJ2G8JQg2fLUZdmHcl1W4rUs6EsdtU")
supabase: Client = create_client(url, key)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(email, password):
    hashed_password = hash_password(password)
    print(f"Checking credentials for email: {email}, hashed password: {hashed_password[:10]}...")
    response = supabase.table("users").select("*").eq("email", email).eq("password", hashed_password).execute()
    print(f"Query response: {response.data}")
    data = response.data
    return data[0] if data else None

def create_user(username, email, password, user_type):
    hashed_password = hash_password(password)
    print(f"Checking for existing user with email: {email}, user_type: {user_type}")
    response = supabase.table("users").select("email").eq("email", email).eq("user_type", user_type).execute()
    print(f"Existing user check response: {response.data}")
    if response.data:
        print(f"User with email {email} and user_type {user_type} already exists")
        return False
    supabase.table("users").insert({
        "username": username,
        "email": email,
        "password": hashed_password,
        "user_type": user_type,
        "created_at": datetime.now().isoformat()
    }).execute()
    print(f"Created user: {username}, {email}, {user_type}")
    return True


# import sqlite3
# import hashlib
# from datetime import datetime

# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# def check_credentials(email, password):
#     conn = sqlite3.connect('recruitment.db')
#     c = conn.cursor()
#     c.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
#               (email, hash_password(password)))
#     user = c.fetchone()
#     conn.close()
#     return user

# def create_user(username, email, password, user_type):
#     conn = sqlite3.connect('recruitment.db')
#     c = conn.cursor()
#     try:
#         c.execute("INSERT INTO users (username, email, password, user_type, created_at) VALUES (?, ?, ?, ?, ?)",
#                   (username, email, hash_password(password), user_type, datetime.now()))
#         conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False
#     finally:
#         conn.close()