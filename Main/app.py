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

# Initialize database
init_db()

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'signup_data' not in st.session_state:
    st.session_state.signup_data = None
if 'verification_code' not in st.session_state:
    st.session_state.verification_code = None

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email(email, code):
    try:
        msg = MIMEText(f"Your verification code is: {code}")
        msg['Subject'] = 'Verify Your Email'
        msg['From'] = st.secrets["GMAIL_USER"]
        msg['To'] = email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(st.secrets["GMAIL_USER"], st.secrets["GMAIL_APP_PASSWORD"])
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send verification email: {str(e)}")
        return False

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



def main():
    if st.session_state.user is None:
        
        # === SIMPLE & BEAUTIFUL TITLE ===
        st.markdown("<h1 style='text-align: center; color: #1e40af; font-size: 50px; font-weight: 800;'>SkillFit AI</h1>", 
                    unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #4b5563; font-size: 18px;'>AI-Powered Hiring & Job Matching</p>", 
                    unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.page == 'login':
            st.subheader("Welcome Back!")

            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            # === FULL-WIDTH BLUE LOGIN BUTTON ===
            if st.button("Login", key="login", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    user = check_credentials(email, password)
                    if user:
                        st.session_state.user = {
                            'id': user['id'],
                            'email': user['email'],
                            'username': user['username'],
                            'user_type': user['user_type']
                        }
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

            # === SIMPLE BLUE LINK FOR SIGNUP ===
            st.markdown("<p style='text-align: center; margin-top: 20px;'>"
                        "Don't have an account? "
                        "<a href='#' style='color: #3b82f6; font-weight: bold; text-decoration: none;'>Sign up</a>"
                        "</p>", unsafe_allow_html=True)

            # Hidden button to catch the link click
            if st.button("Go to Signup", key="hidden_signup", help="Triggered by link click"):
                st.session_state.page = 'signup'
                st.rerun()

        # === SIGNUP PAGE - SAME STYLE ===
        elif st.session_state.page == 'signup':
            st.subheader("Create Your Account")

            username = st.text_input("User Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            user_type = st.selectbox("I am a", ["Recruiter", "Candidate"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Send Verification Code", use_container_width=True):
                    if not username or not email or not password:
                        st.error("Please fill in all fields")
                    elif not is_valid_email(email):
                        st.error("Invalid email address")
                    elif len(password) < 6:
                        st.error("Password must be 6+ characters")
                    else:
                        st.session_state.signup_data = {
                            'username': username, 'email': email,
                            'password': password, 'user_type': user_type
                        }
                        code = generate_verification_code()
                        st.session_state.verification_code = code
                        if send_verification_email(email, code):
                            st.session_state.page = 'verify'
                            st.rerun()
                        else:
                            st.error("Failed to send code")

            with col2:
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.page = 'login'
                    st.rerun()

            # === BACK TO LOGIN LINK ===
            st.markdown("<p style='text-align: center; margin-top: 20px;'>"
                        "Already have an account? "
                        "<a href='#' style='color: #3b82f6; font-weight: bold; text-decoration: none;'>Log in</a>"
                        "</p>", unsafe_allow_html=True)

            if st.button("Go to Login", key="hidden_login"):
                st.session_state.page = 'login'
                st.rerun()

        # === VERIFY PAGE - SAME CLEAN LOOK ===
        elif st.session_state.page == 'verify':
            st.subheader("Check Your Email")

            code_input = st.text_input("Enter 6-digit code")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Verify", use_container_width=True, type="primary"):
                    if code_input == st.session_state.verification_code:
                        signup_data = st.session_state.signup_data
                        if create_user(signup_data['username'], signup_data['email'],
                                     signup_data['password'], signup_data['user_type']):
                            st.success("Account created! Please login.")
                            st.session_state.clear()
                            st.session_state.page = 'login'
                            st.rerun()
                        else:
                            st.error("Email already used")
                    else:
                        st.error("Wrong code")

            with col2:
                if st.button("Back to Signup", use_container_width=True):
                    st.session_state.page = 'signup'
                    st.rerun()

    else:
        # Logged in
        if st.session_state.user['user_type'] == "Recruiter":
            recruiter_interface()
        else:
            candidate_interface()
