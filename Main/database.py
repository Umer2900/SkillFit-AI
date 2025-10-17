from supabase import create_client, Client
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from Streamlit secrets
load_dotenv()

# Initialize Supabase client using secrets
url = os.environ.get("SUPABASE_URL", "https://tzjrpockqmevrcfqxmuw.supabase.co")
key = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR6anJwb2NrcW1ldnJjZnF4bXV3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA1ODE2MjYsImV4cCI6MjA3NjE1NzYyNn0.QFUjG7-JW_w9DoJ2G8JQg2fLUZdmHcl1W4rUs6EsdtU")
supabase: Client = create_client(url, key)

def init_db():
    # Health check to ensure tables exist
    try:
        supabase.table("users").select("id").limit(1).execute()
        supabase.table("resumes").select("id").limit(1).execute()
    except Exception as e:
        raise Exception("Database initialization failed: Tables 'users' or 'resumes' are missing or misconfigured. Please create them in the Supabase dashboard with the correct schema: 'users' (id, email, username, password, user_type, created_at) and 'resumes' (id, user_id, filename, file_content, upload_date, analysis).")

def save_resume(user_id, file):
    filename = file.name
    file_content = file.getvalue()
    supabase.table("resumes").insert({
        "user_id": user_id,
        "filename": filename,
        "file_content": file_content,
        "upload_date": datetime.now()
    }).execute()

def get_user_resumes(user_id):
    response = supabase.table("resumes").select("*").eq("user_id", user_id).execute()
    resumes = response.data
    parsed_resumes = [(resume["id"], resume["filename"], resume["upload_date"], resume["file_content"], resume["analysis"]) for resume in resumes]
    return parsed_resumes

def download_resume(resume_id):
    response = supabase.table("resumes").select("filename, file_content").eq("id", resume_id).execute()
    data = response.data
    if data:
        return data[0]["filename"], data[0]["file_content"]
    return None, None

def clear_resumes(user_id):
    supabase.table("resumes").delete().eq("user_id", user_id).execute()

def delete_account(user_id):
    supabase.table("resumes").delete().eq("user_id", user_id).execute()
    supabase.table("users").delete().eq("id", user_id).execute()

# import sqlite3
# from datetime import datetime

# def init_db():
#     conn = sqlite3.connect('recruitment.db')
#     c = conn.cursor()
    
#     # Create tables
#     c.execute('''CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         email TEXT UNIQUE,
#         username TEXT,
#         password TEXT,
#         user_type TEXT,
#         created_at TIMESTAMP
#     )''')
    
#     c.execute('''CREATE TABLE IF NOT EXISTS resumes (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         user_id INTEGER,
#         filename TEXT,
#         file_content BLOB,
#         upload_date TIMESTAMP,
#         analysis TEXT,
#         FOREIGN KEY(user_id) REFERENCES users(id)
#     )''')
    
#     conn.commit()
#     conn.close()

# # Initialize the database when the module is imported
# init_db()

# def save_resume(user_id, file):
#     filename = file.name
#     file_content = file.getvalue()  # Get raw file content as bytes
    
#     conn = sqlite3.connect('recruitment.db')
#     c = conn.cursor()
#     c.execute("INSERT INTO resumes (user_id, filename, file_content, upload_date) VALUES (?, ?, ?, ?)",
#               (user_id, filename, sqlite3.Binary(file_content), datetime.now()))
#     conn.commit()
#     conn.close()

# def get_user_resumes(user_id):
#     conn = sqlite3.connect('recruitment.db')
#     c = conn.cursor()
#     c.execute("SELECT id, filename, upload_date, file_content, analysis FROM resumes WHERE user_id = ?", (user_id,))
#     resumes = c.fetchall()
#     conn.close()
#     # Prepare resumes with file content for download
#     parsed_resumes = []
#     for resume in resumes:
#         parsed_resumes.append((resume[0], resume[1], resume[2], resume[3], resume[4]))
#     return parsed_resumes

# def download_resume(resume_id):
#     conn = sqlite3.connect('recruitment.db')
#     c = conn.cursor()
#     c.execute("SELECT filename, file_content FROM resumes WHERE id = ?", (resume_id,))
#     result = c.fetchone()
#     conn.close()
#     if result:
#         filename, file_content = result
#         return filename, file_content
#     return None, None

# def clear_resumes(user_id):
#     conn = sqlite3.connect('recruitment.db')
#     c = conn.cursor()
#     c.execute("DELETE FROM resumes WHERE user_id = ?", (user_id,))
#     conn.commit()
#     conn.close()

# def delete_account(user_id):
#     conn = sqlite3.connect('recruitment.db')
#     c = conn.cursor()
    
#     # Delete associated resumes first due to foreign key constraint
#     c.execute("DELETE FROM resumes WHERE user_id = ?", (user_id,))
    
#     # Delete the user
#     c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
#     conn.commit()
#     conn.close()



