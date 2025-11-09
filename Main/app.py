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
#         msg['From'] = st.secrets["GMAIL_USER"]
#         msg['To'] = email
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#             server.login(st.secrets["GMAIL_USER"], st.secrets["GMAIL_APP_PASSWORD"])
#             server.send_message(msg)
#         return True
#     except Exception as e:
#         st.error(f"Failed to send verification email: {str(e)}")
#         return False

# def main():
#     if st.session_state.user is None:
#         if st.session_state.page == 'login':
#             # st.title("Login")
#             st.title("SkillFit AI")
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.button("Login"):
#                     user = check_credentials(email, password)
#                     if user:
#                         st.session_state.user = {
#                             'id': user['id'],
#                             'email': user['email'],
#                             'username': user['username'],
#                             'user_type': user['user_type']
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
#                             st.error("This email is already registered for the selected user type.")
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




# app.py - FINAL: REAL BLUE LINKS THAT WORK IN SAME TAB (NO BUTTONS, NO NEW TAB)
import streamlit as st
from auth import check_credentials, create_user
from database import init_db
from interfaces.Recruiter import recruiter_interface
from interfaces.Candidate import candidate_interface
import re
import random
import string
import smtplib
from email.mime.text import MIMEText

init_db()

# Session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'signup_data' not in st.session_state:
    st.session_state.signup_data = None
if 'verification_code' not in st.session_state:
    st.session_state.verification_code = None

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    try:
        msg = MIMEText(f"Your SkillFit AI code: {code}")
        msg['Subject'] = 'SkillFit AI - Verify Email'
        msg['From'] = st.secrets["GMAIL_USER"]
        msg['To'] = email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(st.secrets["GMAIL_USER"], st.secrets["GMAIL_APP_PASSWORD"])
            server.send_message(msg)
        return True
    except:
        st.error("Email failed")
        return False

# === MAIN ===
def main():
    # Check URL parameter ONCE at top
    params = st.query_params
    if params.get("page") == "signup":
        st.session_state.page = "signup"
        st.query_params.clear()
    elif params.get("page") == "login":
        st.session_state.page = "login"
        st.query_params.clear()

    if st.session_state.user is None:
        # TITLE
        st.markdown("<h1 style='text-align:center; color:#1e40af; font-size:52px; font-weight:900;'>SkillFit AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#555; font-size:20px; margin-bottom:40px;'>AI-Powered Hiring & Job Matching</p>", unsafe_allow_html=True)

        # LOGIN PAGE
        if st.session_state.page == 'login':
            st.markdown("### Welcome Back")

            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Login", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Fill both fields")
                else:
                    user = check_credentials(email, password)
                    if user:
                        st.session_state.user = user
                        st.success("Logged in!")
                        st.rerun()
                    else:
                        st.error("Wrong credentials")

            # REAL WORKING LINK - SAME TAB
            st.markdown("""
            <div style="text-align:center; margin-top:30px; font-size:16px;">
                Don't have an account? 
                <a href="/?page=signup" style="color:#2563eb; font-weight:bold; text-decoration:none;">
                    Sign up here
                </a>
            </div>
            """, unsafe_allow_html=True)

        # SIGNUP PAGE
        elif st.session_state.page == 'signup':
            st.markdown("### Create Account")

            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            user_type = st.selectbox("I am a", ["Recruiter", "Candidate"])

            if st.button("Send Verification Code", use_container_width=True, type="primary"):
                if not all([username, email, password]):
                    st.error("All fields required")
                elif not is_valid_email(email):
                    st.error("Invalid email")
                elif len(password) < 6:
                    st.error("Password too short")
                else:
                    st.session_state.signup_data = {"username": username, "email": email, "password": password, "user_type": user_type}
                    code = generate_verification_code()
                    st.session_state.verification_code = code
                    if send_verification_email(email, code):
                        st.success("Code sent!")
                        st.session_state.page = 'verify'
                        st.rerun()

            # REAL WORKING LOGIN LINK
            st.markdown("""
            <div style="text-align:center; margin-top:30px; font-size:16px;">
                Already have an account? 
                <a href="/?page=login" style="color:#2563eb; font-weight:bold; text-decoration:none;">
                    Log in
                </a>
            </div>
            """, unsafe_allow_html=True)

        # VERIFY PAGE
        elif st.session_state.page == 'verify':
            st.markdown("### Verify Email")
            st.info("Check your email")

            code = st.text_input("6-digit code")
            if st.button("Verify", use_container_width=True, type="primary"):
                if code == st.session_state.verification_code:
                    data = st.session_state.signup_data
                    if create_user(data['username'], data['email'], data['password'], data['user_type']):
                        st.success("Done! Logging in...")
                        st.session_state.clear()
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error("Email already used")
                else:
                    st.error("Wrong code")

    else:
        if st.session_state.user['user_type'] == "Recruiter":
            recruiter_interface()
        else:
            candidate_interface()

if __name__ == "__main__":
    main()