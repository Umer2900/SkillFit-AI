import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        username TEXT,
        password TEXT,
        user_type TEXT,
        created_at TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        file_content BLOB,
        upload_date TIMESTAMP,
        analysis TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()

# Initialize the database when the module is imported
init_db()

def save_resume(user_id, file):
    filename = file.name
    file_content = file.getvalue()  # Get raw file content as bytes
    
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    c.execute("INSERT INTO resumes (user_id, filename, file_content, upload_date) VALUES (?, ?, ?, ?)",
              (user_id, filename, sqlite3.Binary(file_content), datetime.now()))
    conn.commit()
    conn.close()

def get_user_resumes(user_id):
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    c.execute("SELECT id, filename, upload_date, file_content, analysis FROM resumes WHERE user_id = ?", (user_id,))
    resumes = c.fetchall()
    conn.close()
    # Prepare resumes with file content for download
    parsed_resumes = []
    for resume in resumes:
        parsed_resumes.append((resume[0], resume[1], resume[2], resume[3], resume[4]))
    return parsed_resumes

def download_resume(resume_id):
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    c.execute("SELECT filename, file_content FROM resumes WHERE id = ?", (resume_id,))
    result = c.fetchone()
    conn.close()
    if result:
        filename, file_content = result
        return filename, file_content
    return None, None

def clear_resumes(user_id):
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    c.execute("DELETE FROM resumes WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def delete_account(user_id):
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    
    # Delete associated resumes first due to foreign key constraint
    c.execute("DELETE FROM resumes WHERE user_id = ?", (user_id,))
    
    # Delete the user
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    conn.commit()
    conn.close()



