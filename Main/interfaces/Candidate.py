import streamlit as st
import pandas as pd
import os
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from Gemini_services.services import parse_resume_for_candidate

# Function to convert PDF to text
def pdf_to_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Load the dataset
# df = pd.read_csv("Web_Scrapping/job_descriptions.csv")
# get absolute path to project root (one level above 'Main')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "Web_Scrapping", "job_descriptions.csv")
df = pd.read_csv(CSV_PATH)

df.fillna("", inplace=True)

# Combine JobRole, Experience, and Skills to form job_description
# Boost experience by repeating it 3 times
df['job_description'] = (
    df['Experience'] + ' ' + df['Experience'] + ' ' + df['Experience'] + ' ' +
    df['Skills'] + ' ' +
    df['JobRole']
)

# Streamlit UI for Candidate
def candidate_interface():
    st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
    menu = ["Homepage", "Job Recommendation", "More"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Homepage":
        st.title("Candidate Homepage")
        # st.subheader(f"Welcome to SkillFit AI, {st.session_state.user['username']}!")

        st.markdown("""
        ### Welcome to SkillFit AI — Your Personal Job-Fit Superpower

        **Stop guessing. Stop applying blindly. Start winning.**

        You don't need to send 100 applications to get 1 interview.  
        You just need **one perfect match** — and SkillFit AI finds it for you in seconds.


        #### One Upload → Your Entire Career Strategy

        **Job Recommendation System**  
        Upload **your resume (PDF)** → Click **“Find Jobs”** → Get this:

        - Top 5 jobs **perfectly matched** to your skills, experience & role  
        - Real company names, locations, salaries (when available)  
        - Direct **“Apply Here”** links — no copy-paste, no login traps  
        - Powered by **Google Gemini AI** — smarter than any job board

        No spam. No fake listings. Just **jobs you're actually qualified for**.


        #### Why Candidates Trust SkillFit AI

        - **No more rejection silence** — apply only where you're a **strong fit**  
        - **Save 20+ hours per week** — stop scrolling Indeed & LinkedIn  
        - **Beat ATS filters** — we show you jobs that value your real skills  
        - **100% private** — your resume is analyzed once, then deleted  
        - **Works for freshers & 15+ year veterans** — no bias, no limits


        #### Your Next Step is Simple

        1. Go to **“Job Recommendation”** in the sidebar  
        2. Upload your latest resume (PDF)  
        3. Click **“Find Jobs”**  
        4. Apply to the top matches with **one click**

        That's it.

        **No profile setup. No premium subscription. No nonsense.**

        **You focus on growing your career.**  
        **Let SkillFit AI open the right doors.**

        Your dream job isn't hiding — it's waiting.  
        Upload your resume now and let's go get it
        """)
    
    elif choice == "Job Recommendation":
        st.title("Job Recommendation System")
        uploaded_file = st.file_uploader("Choose a resume file", type=['pdf'])
        resume_text = ""
        parsed_resume_text = ""

        if uploaded_file is not None:
            # Extract RAW text from the uploaded PDF
            resume_text = pdf_to_text(uploaded_file)

            # Parse the resume text using Gemini API
            try:
                parsed_resume_text = parse_resume_for_candidate(resume_text)
                # Optional: Show the parsed resume text
                # st.subheader("Parsed Resume Text")
                # st.text(parsed_resume_text)
            except Exception as e:
                st.error(f"Error parsing resume: {str(e)}")
                return

        if st.button("Find Jobs"):
            if parsed_resume_text.strip() != "":
                # Vectorize job descriptions and parsed resume text
                vectorizer = TfidfVectorizer()
                job_vectors = vectorizer.fit_transform(df['job_description'])
                resume_vector = vectorizer.transform([parsed_resume_text])

                # Calculate similarity
                similarity = cosine_similarity(resume_vector, job_vectors)
                top_indices = similarity[0].argsort()[-5:][::-1]
                top_jobs = df.iloc[top_indices][['CompanyName', 'JobRole', 'Experience', 'Skills', 'Links']]

                # Make Links clickable
                def make_clickable(link):
                    return f'<a href="{link}" target="_blank">Apply Here</a>'

                top_jobs['Apply'] = top_jobs['Links'].apply(make_clickable)

                # Remove old 'Links' column
                top_jobs = top_jobs.drop(columns=['Links'])

                # Display as HTML table
                st.markdown(
                    top_jobs.to_html(escape=False, index=False),
                    unsafe_allow_html=True
                )
            else:
                st.warning("Please upload a resume file.")
    
    elif choice == "More":
        st.title("More Options")
        st.write("Select an action below:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Logout"):
                st.session_state.user = None
                st.session_state.page = 'login'
                st.success("Logged out successfully!")
                st.rerun()
        with col2:
            if st.button("Delete Account"):
                user_id = st.session_state.user['id']
                delete_account(user_id)
                st.session_state.user = None
                st.session_state.page = 'login'
                st.success("Account deleted successfully!")
                st.rerun()