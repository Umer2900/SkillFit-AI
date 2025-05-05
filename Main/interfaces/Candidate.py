import streamlit as st
import pandas as pd
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import save_resume, get_user_resumes, delete_account
from datetime import datetime
from Gemini_services.gemini_services import parse_resume_for_candidate

# Function to convert PDF to text
def pdf_to_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Load the dataset
df = pd.read_csv("Web_Scrapping/job_descriptions.csv")
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
        st.subheader(f"Welcome to SkillFit AI, {st.session_state.user['username']}!")
        st.markdown("""
        ### Your Journey to the Perfect Job Starts Here

        As a candidate, you're on a mission to find a job that matches your skills, experience, and aspirations. **SkillFit AI** is here to help you every step of the way! Powered by the Gemini API, our platform uses advanced AI to analyze your resume and recommend the best job opportunities tailored just for you. Say goodbye to endless job searches—let us do the heavy lifting while you focus on landing your dream role.

        #### What You Can Do Here

        **SkillFit AI** offers a personalized experience for candidates through two key sections accessible from the sidebar:

        1. **Job Recommendation**  
           - **What It Does**: Upload your resume, and our AI will analyze it to extract your job role, experience, and skills. Using this information, we match you with the top 5 job opportunities from our curated job dataset. Each recommendation includes the job title, company, location, and a direct link to apply.  
           - **Why It's Useful**: Save time by focusing on jobs that are the best fit for your profile. Our AI-driven matching ensures you're applying to roles where you're most likely to succeed, based on your skills and experience.  
           - **How to Use It**: Navigate to “Job Recommendation,” upload your resume (PDF), and click “Find Jobs” to see your personalized job matches. Click the links to apply directly!

        2. **More Options**  
           - **What It Does**: Manage your account with options to log out or delete your account.  
           - **Why It's Useful**: Keep your account secure by logging out when you're done. If you no longer need your account, the “Delete Account” option ensures your data is permanently removed.  
           - **How to Use It**: Go to “More,” then choose “Logout” to end your session or “Delete Account” to remove your profile.

        #### Why Choose SkillFit AI?
        - **Personalized Job Matches**: Our AI, powered by the Gemini API, ensures you get recommendations that truly align with your profile.  
        - **Effortless Job Search**: No more scrolling through irrelevant listings—get the best matches in seconds.  
        - **Seamless Experience**: Our user-friendly interface makes it easy to upload your resume, find jobs, and apply with just a few clicks.  

        Ready to take the next step in your career? Use the sidebar to explore the features and find your perfect job today!
        """)
    
    elif choice == "Job Recommendation":
        st.title("Job Recommendation System")
        uploaded_file = st.file_uploader("Choose a resume file", type=['pdf'])
        resume_text = ""
        parsed_resume_text = ""

        if uploaded_file is not None:
            # Extract raw text from the uploaded PDF
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