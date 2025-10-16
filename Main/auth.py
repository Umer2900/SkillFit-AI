# auth.py
import bcrypt
from database import supabase_client

def hash_password(password):
    """Hashes the password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_password, provided_password):
    """Verifies a password against a stored hash."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def signup_user(username, password):
    """Signs up a new user."""
    # Check if user already exists
    response = supabase_client.table('users').select('id').eq('username', username).execute()
    if response.data:
        return False, "Username already exists."

    # Hash password and add new user
    hashed_password = hash_password(password).decode('utf-8')
    insert_response = supabase_client.table('users').insert({
        'username': username,
        'password': hashed_password
    }).execute()

    if insert_response.data:
        return True, "Signup successful! Please log in."
    else:
        return False, "An error occurred during signup."

def login_user(username, password):
    """Logs in an existing user."""
    response = supabase_client.table('users').select('id, password').eq('username', username).execute()

    if not response.data:
        return False, None

    user_data = response.data[0]
    stored_password = user_data['password']

    if verify_password(stored_password, password):
        return True, user_data['id']  # Return the user ID on successful login
    else:
        return False, None

def get_user_id(username):
    """Retrieves the user ID for a given username."""
    response = supabase_client.table('users').select('id').eq('username', username).execute()
    if response.data:
        return response.data[0]['id']
    return None



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