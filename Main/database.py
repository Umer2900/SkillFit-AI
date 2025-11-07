from supabase import create_client, Client
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from Streamlit secrets
load_dotenv()

# Initialize Supabase client using secrets
url = os.environ.get("SUPABASE_URL", "https://tzjrpockqmevrcfqxmuw.supabase.co")
key = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR6anJwb2NrcW1ldnJjZnF4bXV3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA1ODE2MjYsImV4cCI6MjA3NjE1NzYyNn0.QFUjG7-JW_w9DoJ2G8JQg2fLUZdmHcl1W4rUs6EsdtU")
supabase: Client = create_client(url, key)

def init_db():
    # Enhanced retry logic for transient errors
    max_retries = 5
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Checking database tables...")
            supabase.table("users").select("id").limit(1).execute()
            supabase.table("resumes").select("id").limit(1).execute()
            logger.info("Database initialization successful.")
            return
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            raise Exception("Database initialization failed: Tables 'users' or 'resumes' are missing or misconfigured. Please create them in the Supabase dashboard with the correct schema: 'users' (id, email, username, password, user_type, created_at) and 'resumes' (id, user_id, filename, file_content, upload_date, analysis).")


def delete_account(user_id):
    supabase.table("resumes").delete().eq("user_id", user_id).execute()
    supabase.table("users").delete().eq("id", user_id).execute()