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
        # === CUSTOM CSS FOR BEAUTIFUL UI ===
        st.markdown("""
        <style>
            .main {background-color: #f8f9fa;}
            .title {
                font-size: 48px !important;
                font-weight: 800 !important;
                background: linear-gradient(90deg, #1e40af, #3b82f6, #60a5fa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-align: center;
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                color: #4b5563;
                font-size: 18px;
                margin-bottom: 40px;
            }
            .full-width-button {
                background: linear-gradient(90deg, #1e40af, #3b82f6);
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 12px;
                padding: 14px;
                font-size: 18px;
            }
            .full-width-button:hover {
                background: linear-gradient(90deg, #1e3a8a, #2563eb);
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
            }
            .signup-link {
                text-align: center;
                margin-top: 20px;
                font-size: 16px;
            }
            .signup-link a {
                color: #3b82f6;
                font-weight: 600;
                text-decoration: none;
            }
            .signup-link a:hover {
                color: #1e40af;
                text-decoration: underline;
            }
            .stButton > button {
                width: 100%;
            }
        </style>
        """, unsafe_allow_html=True)

        if st.session_state.page == 'login':
            st.markdown("<h1 class='title'>SkillFit AI</h1>", unsafe_allow_html=True)
            st.markdown("<p class='subtitle'>AI-Powered Hiring & Job Matching Platform</p>", unsafe_allow_html=True)

            with st.container():
                email = st.text_input("Email", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")

                if st.button("Login", key="login_btn"):
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

                st.markdown("""
                <div class="signup-link">
                    Don't have an account? <a href="#" id="signup_link">Sign up</a>
                </div>
                """, unsafe_allow_html=True)

                # Hidden button to trigger signup via link
                if st.button("Go to Signup", key="hidden_signup", help="Triggered by link"):
                    st.session_state.page = 'signup'
                    st.rerun()

        elif st.session_state.page == 'signup':
            st.markdown("<h1 class='title'>SkillFit AI</h1>", unsafe_allow_html=True)
            st.markdown("<p class='subtitle'>Join thousands of recruiters & candidates</p>", unsafe_allow_html=True)

            with st.container():
                username = st.text_input("User Name", placeholder="Choose a username")
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
                user_type = st.selectbox("I am a", ["Recruiter", "Candidate"])

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Send Verification Code", key="send_code"):
                        if not username or not email or not password:
                            st.error("Please fill in all fields")
                        elif not is_valid_email(email):
                            st.error("Please enter a valid email address")
                        elif len(password) < 6:
                            st.error("Password must be at least 6 characters long")
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
                                st.error("Failed to send verification email.")

                with col2:
                    if st.button("Back to Login", key="back_login"):
                        st.session_state.page = 'login'
                        st.rerun()

                st.markdown("""
                <div class="signup-link">
                    Already have an account? <a href="#" id="login_link">Log in</a>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Go to Login", key="hidden_login"):
                    st.session_state.page = 'login'
                    st.rerun()

        elif st.session_state.page == 'verify':
            st.markdown("<h1 class='title'>SkillFit AI</h1>", unsafe_allow_html=True)
            st.markdown("<p class='subtitle'>Verify your email to continue</p>", unsafe_allow_html=True)

            code_input = st.text_input("Enter Verification Code", placeholder="123456")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Verify", key="verify"):
                    if code_input == st.session_state.verification_code:
                        signup_data = st.session_state.signup_data
                        if create_user(
                            signup_data['username'], signup_data['email'],
                            signup_data['password'], signup_data['user_type']
                        ):
                            st.success("Account created! Please login.")
                            st.session_state.signup_data = None
                            st.session_state.verification_code = None
                            st.session_state.page = 'login'
                            st.rerun()
                        else:
                            st.error("This email is already registered.")
                    else:
                        st.error("Invalid verification code")

            with col2:
                if st.button("Back to Signup", key="back_signup"):
                    st.session_state.page = 'signup'
                    st.rerun()

    else:
        user_type = st.session_state.user['user_type']
        if user_type == "Recruiter":
            recruiter_interface()
        else:
            candidate_interface()
