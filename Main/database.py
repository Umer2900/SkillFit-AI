import time
import logging
import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client using env
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
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