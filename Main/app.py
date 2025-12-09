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
        msg = MIMEText(f"Your SkillFit AI verification code is: {code}")
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
    if st.session_state.user is None:
        # TITLE
        st.markdown("<h1 style='text-align:center; color:#1e40af; font-size:52px; font-weight:900;'>SkillFit AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#555; font-size:20px; margin-bottom:40px;'>AI-Powered Hiring & Job Matching</p>", unsafe_allow_html=True)

        # === LOGIN PAGE ===
        if st.session_state.page == 'login':
            email = st.text_input("Email", placeholder="abc@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            if st.button("Login", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill both fields")
                else:
                    user = check_credentials(email, password)
                    if user:
                        st.session_state.user = user
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Don't have an account? → Go to Signup", use_container_width=True):
                st.session_state.page = 'signup'
                st.rerun()

        # === SIGNUP PAGE ===
        elif st.session_state.page == 'signup':
            st.markdown("### Create Your Account")
            username = st.text_input("Username", placeholder="Enter your username")
            email = st.text_input("Email", placeholder="abc@example.com")
            password = st.text_input("Password", type="password", placeholder="6+ characters")
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
                        st.success("Code sent to your email!")
                        st.session_state.page = 'verify'
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Already have an account? Back to Login", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()

        # === VERIFY PAGE ===
        elif st.session_state.page == 'verify':
            st.markdown("### Verify Your Email")
            st.info("Check your email for the 6-digit code")

            code = st.text_input("Enter 6-digit code", placeholder="123456")

            if st.button("Verify & Create Account", use_container_width=True, type="primary"):
                if code == st.session_state.verification_code:
                    data = st.session_state.signup_data
                    if create_user(data['username'], data['email'], data['password'], data['user_type']):
                        st.success("Account created successfully!")
                        st.session_state.clear()
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error("Email already registered")
                else:
                    st.error("Invalid code")

            if st.button("← Back to Signup", use_container_width=True):
                st.session_state.page = 'signup'
                st.rerun()

    else:
        # LOGGED IN
        if st.session_state.user['user_type'] == "Recruiter":
            recruiter_interface()
        else:
            candidate_interface()

if __name__ == "__main__":
    main()

## cd "D:\3. Code\Main" 
## RUN:  streamlit run app.py       