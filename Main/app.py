import sys
import os

# This allows imports from other modules in the same directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))


import streamlit as st
from PyPDF2 import PdfReader
# from Gemini_services import get_gemini_response, input_pdf_text
from Gemini_services.gemini_services import get_gemini_response, input_pdf_text
from auth import login_user, signup_user
from database import supabase_client

# --- Page Configuration ---
st.set_page_config(page_title="SkillFit AI", page_icon="🤖", layout="wide")

# --- Helper Functions ---
def save_resume_data(user_id, resume_text, jd_text, score, feedback):
    """Saves the resume analysis data to Supabase."""
    try:
        response = supabase_client.table('resumes').insert({
            'user_id': user_id,
            'resume_text': resume_text,
            'jd_text': jd_text,
            'score': int(score),
            'feedback': feedback
        }).execute()
        return response
    except Exception as e:
        st.error(f"Failed to save data: {e}")
        return None

def get_resumes_for_user(user_id):
    """Retrieves all resume analyses for a given user from Supabase."""
    try:
        response = supabase_client.table('resumes').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Failed to retrieve data: {e}")
        return []

# --- Session State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# --- UI Sections ---

# --- Sidebar for Login/Signup ---
with st.sidebar:
    st.title("Welcome to SkillFit AI")

    if st.session_state['logged_in']:
        st.success(f"Logged in as **{st.session_state['username']}**")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = None
            st.session_state['username'] = ""
            st.rerun()

    else:
        choice = st.selectbox("Login / Signup", ["Login", "Signup"])

        with st.form("auth_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button(label=choice)

            if submit_button:
                if choice == "Signup":
                    success, message = signup_user(username, password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else: # Login
                    logged_in, user_id = login_user(username, password)
                    if logged_in:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user_id
                        st.session_state['username'] = username
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

# --- Main Application ---
if st.session_state['logged_in']:
    st.title("📄 Resume Analysis Tool")
    st.markdown("Get instant feedback on your resume against any job description.")

    # Main application layout
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Your Inputs")
        jd = st.text_area("Paste the Job Description here", height=200)
        uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf")

        submit = st.button("Analyze My Resume")

    with col2:
        st.header("Analysis Result")
        if submit:
            if uploaded_file is not None and jd:
                with st.spinner("Analyzing..."):
                    try:
                        resume_text = input_pdf_text(uploaded_file)
                        response_content = get_gemini_response(resume_text, jd)

                        # Extracting parts from the response
                        # Ensure your Gemini prompt returns data in a parsable format
                        # Example: "Score: 85\nFeedback: Your feedback here..."
                        score_line = next((line for line in response_content.split('\n') if "Score:" in line), None)
                        feedback_line = response_content.split("Feedback:")[1] if "Feedback:" in response_content else response_content

                        if score_line:
                            score = score_line.split(":")[1].strip()
                            st.subheader(f"ATS Match Score: {score}%")
                        else:
                            score = 0
                            st.warning("Could not determine score.")

                        st.subheader("Detailed Feedback:")
                        st.markdown(feedback_line)

                        # Save to database
                        save_resume_data(st.session_state['user_id'], resume_text, jd, score, feedback_line)

                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please upload a resume and paste the job description.")

    # Display past results
    st.markdown("---")
    st.header("Your Past Analyses")
    past_resumes = get_resumes_for_user(st.session_state['user_id'])

    if past_resumes:
        for i, resume in enumerate(past_resumes):
            with st.expander(f"Analysis from {resume['created_at'].split('T')[0]} - Score: {resume['score']}%"):
                st.subheader("Job Description")
                st.text_area("JD", value=resume['jd_text'], height=150, key=f"jd_{i}", disabled=True)
                st.subheader("Feedback Received")
                st.markdown(resume['feedback'])
    else:
        st.info("You have no past analyses saved.")

else:
    st.title("Please Login to Continue")
    st.info("Use the sidebar to log in or create a new account.")




# import streamlit as st
# from auth import check_credentials, create_user
# from database import init_db
# from interfaces.Recruiter import recruiter_interface
# from interfaces.Candidate import candidate_interface
# import re
# import random
# import string
# import smtplib
# from email.mime.text import MIMEText
# # from os import environ

# # Initialize database
# init_db()

# # Session state initialization
# if 'user' not in st.session_state:
#     st.session_state.user = None
# if 'page' not in st.session_state:
#     st.session_state.page = 'login'
# if 'signup_data' not in st.session_state:
#     st.session_state.signup_data = None
# if 'verification_code' not in st.session_state:
#     st.session_state.verification_code = None

# def is_valid_email(email):
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None

# def generate_verification_code(length=6):
#     return ''.join(random.choices(string.digits, k=length))

# def send_verification_email(email, code):
#     try:
#         msg = MIMEText(f"Your verification code is: {code}")
#         msg['Subject'] = 'Verify Your Email'
#         # msg['From'] = environ.get('GMAIL_USER')           
#         msg['From'] = st.secrets["GMAIL_USER"]          # to pull secrets from Streamlit's manager instead of the environment.
#         msg['To'] = email
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#             # server.login(environ.get('GMAIL_USER'), environ.get('GMAIL_APP_PASSWORD'))
#             server.login(st.secrets["GMAIL_USER"], st.secrets["GMAIL_APP_PASSWORD"])
#             server.send_message(msg)
#         return True
#     except Exception as e:
#         st.error(f"Failed to send verification email: {str(e)}")
#         return False

# def main():
#     if st.session_state.user is None:
#         if st.session_state.page == 'login':
#             st.title("Login")
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.button("Login"):
#                     user = check_credentials(email, password)
#                     if user:
#                         st.session_state.user = {
#                             'id': user[0],
#                             'email': user[1],
#                             'username': user[2],
#                             'user_type': user[4]
#                         }
#                         st.success("Logged in successfully!")
#                         st.rerun()
#                     else:
#                         st.error("Invalid credentials")
#             with col2:
#                 if st.button("Go to Signup"):
#                     st.session_state.page = 'signup'
#                     st.rerun()
        
#         elif st.session_state.page == 'signup':
#             st.title("Signup")
#             username = st.text_input("User Name")
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             user_type = st.selectbox("User Type", ["Recruiter", "Candidate"])
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.button("Send Verification Code"):
#                     if not username or not email or not password:
#                         st.error("Please fill in all fields")
#                     elif not is_valid_email(email):
#                         st.error("Please enter a valid email address")
#                     elif len(password) < 6:
#                         st.error("Password must be at least 6 characters long")
#                     else:
#                         st.session_state.signup_data = {
#                             'username': username,
#                             'email': email,
#                             'password': password,
#                             'user_type': user_type
#                         }
#                         code = generate_verification_code()
#                         st.session_state.verification_code = code
#                         if send_verification_email(email, code):
#                             st.session_state.page = 'verify'
#                             st.rerun()
#                         else:
#                             st.error("Failed to send verification email. Please try again.")
#             with col2:
#                 if st.button("Back to Login"):
#                     st.session_state.page = 'login'
#                     st.rerun()
        
#         elif st.session_state.page == 'verify':
#             st.title("Verify Email")
#             code_input = st.text_input("Enter Verification Code")
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.button("Verify"):
#                     if code_input == st.session_state.verification_code:
#                         signup_data = st.session_state.signup_data
#                         if create_user(
#                             signup_data['username'],
#                             signup_data['email'],
#                             signup_data['password'],
#                             signup_data['user_type']
#                         ):
#                             st.success("Account created! Please login.")
#                             st.session_state.signup_data = None
#                             st.session_state.verification_code = None
#                             st.session_state.page = 'login'
#                             st.rerun()
#                         else:
#                             st.error("Email already exists")
#                     else:
#                         st.error("Invalid verification code")
#             with col2:
#                 if st.button("Back to Signup"):
#                     st.session_state.page = 'signup'
#                     st.rerun()
    
#     else:
#         user_type = st.session_state.user['user_type']
#         if user_type == "Recruiter":
#             recruiter_interface()
#         else:
#             candidate_interface()

# if __name__ == "__main__":
#     main()

