import sqlite3
import hashlib
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(email, password):
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
              (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username, email, password, user_type):
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, email, password, user_type, created_at) VALUES (?, ?, ?, ?, ?)",
                  (username, email, hash_password(password), user_type, datetime.now()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()