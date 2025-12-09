import hashlib
import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# Initialize Supabase client
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]

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