import os
import json
import numpy as np
import PyPDF2
import pandas as pd
import streamlit as st

from database import delete_account
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from Gemini_services.services import parse_resume_for_candidate

# === PATH SETUP ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "Web_Scrapping", "cleaned_job_descriptions.csv")

df = pd.read_csv(CSV_PATH)
df.fillna("", inplace=True)

# Ensure Experience is numeric
df['Experience'] = pd.to_numeric(df['Experience'], errors='coerce').fillna(0)

# === PDF TO TEXT ===
def pdf_to_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# === CANDIDATE INTERFACE — BEAUTIFUL & POWERFUL ===
def candidate_interface():
    # === SIDEBAR: SKILLFIT AI + USERNAME IN BLUE ===
    st.sidebar.markdown("""
    <h1 style='color: #1e40af; font-size: 28px; font-weight: 900; margin-bottom: 5px;'>
        SkillFit AI
    </h1>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <p style='color: #1e40af; font-size: 20px; font-weight: bold; margin-top: 0;'>
        Hi, {st.session_state.user['username']}!
    </p>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    menu = ["Homepage", "Job Recommendation", "More"]
    choice = st.sidebar.selectbox("Menu", menu, label_visibility="collapsed")

    # === HOMEPAGE ===
    if choice == "Homepage":
        st.markdown("""
        <h1 style='text-align: center; color: #1e40af; font-size: 48px; font-weight: 900;'>
            SkillFit AI
        </h1>
        <p style='text-align: center; color: #555; font-size: 22px; margin-bottom: 40px;'>
            <strong>Your Resume.</strong> Your Superpower. Your Next Job.
        </p>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); padding: 35px; border-radius: 18px; text-align: center; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);">
            <h2 style="color: #1e3a8a; margin: 0;">
                Welcome, <strong style="color: #1e40af; font-size: 28px;">{st.session_state.user['username']}</strong>!
            </h2>
            <p style="font-size: 20px; color: #1e40af; margin: 10px 0;">
                You're <strong>one upload away</strong> from your dream job.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            <div style="background: #f0fdf4; padding: 30px; border-radius: 16px; border-left: 8px solid #22c55e; height: 100%;">
                <h3 style="color: #166534; margin-top: 0;">How It Works</h3>
                <p style="font-size: 17px; line-height: 1.7;">
                    1. Upload your <strong>latest resume (PDF)</strong><br>
                    2. Click <strong>“Find Jobs”</strong><br>
                    3. Get <strong>top 5 perfect matches</strong> with <strong>direct apply links</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="background: #fefce8; padding: 30px; border-radius: 16px; border-left: 8px solid #facc15; height: 100%;">
                <h3 style="color: #854d0e; margin-top: 0;">Why You'll Win</h3>
                <p style="font-size: 17px; line-height: 1.7;">
                    • Apply only where you're <strong>90%+ qualified</strong><br>
                    • Beat ATS filters with <strong>Gemini AI</strong><br>
                    • No fake jobs — real companies, real links<br>
                    • <strong>Zero spam. Zero stress.</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #ecfdf5; padding: 30px; border-radius: 16px; border: 3px dashed #10b981; text-align: center;">
            <h3 style="color: #065f46; margin-top: 0;">Your Resume Is Ready. Are You?</h3>
            <p style="font-size: 19px; color: #065f46;">
                <strong>Stop applying blindly.</strong><br>
                Let AI show you <strong>jobs that want YOU</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <p style="text-align: center; font-size: 22px; color: #1e40af;">
            <strong>Ready to land your next role?</strong><br>
            Go to <strong>Job Recommendation</strong> → Upload → <strong>Win.</strong>
        </p>
        """, unsafe_allow_html=True)

    # === JOB RECOMMENDATION ===
    elif choice == "Job Recommendation":
        st.markdown("<h1 style='color: #1e40af; text-align: center;'>Job Recommendation</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; color: #555;'>Upload your resume → Get your <strong>top 5 perfect jobs</strong> instantly.</p>", unsafe_allow_html=True)
        st.markdown("<br>",  unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=['pdf'], help="We only read it once — never stored")

        # Session state caching
        if 'parsed_resume' not in st.session_state:
            st.session_state.parsed_resume = None
        if 'last_file_name' not in st.session_state:
            st.session_state.last_file_name = None

        
        if uploaded_file is not None:

            # Only call LLM if new file
            if st.session_state.last_file_name != uploaded_file.name:
                with st.spinner("AI is reading your resume..."):
                    resume_text = pdf_to_text(uploaded_file)
                    try:
                        st.session_state.parsed_resume = parse_resume_for_candidate(resume_text)
                        st.session_state.last_file_name = uploaded_file.name
                        st.success("Resume analyzed successfully!")
                    except Exception as e:
                        st.error(e)
                        st.session_state.parsed_resume = None
            
            if st.button("Find My Perfect Jobs", use_container_width=True, type="primary"):

                parsed_resume = st.session_state.parsed_resume

                if parsed_resume:

                    # === Convert LLM output → dict → DataFrame ===
                    parsed_resume_dict = json.loads(parsed_resume)
                    resume_df = pd.DataFrame([parsed_resume_dict])

                    # Skills similarity
                    vectorizer = TfidfVectorizer(stop_words='english')
                    skills_matrix = vectorizer.fit_transform(
                         df['Skills'].astype(str).tolist() +
                        resume_df['Skills'].astype(str).tolist()
                    )

                    cosine_skills = cosine_similarity(
                        skills_matrix[-1],
                        skills_matrix[:-1]
                    ).flatten()

                    # Experience similarity
                    resume_exp = float(resume_df['Experience'].values[0])
                    exp_diff = np.abs(df['Experience'] - resume_exp)
                    cosine_exp = 1 / (1 + exp_diff)

                    # Final score
                    final_scores = 0.3 * cosine_skills + 0.7 * cosine_exp

                    # =========================
                    # 🔝 TOP JOBS
                    # =========================
                    top_indices = final_scores.argsort()[-5:][::-1]

                    top_jobs = df.iloc[top_indices][
                        ['CompanyName', 'JobRole', 'Experience', 'Skills', 'Links']
                    ].copy()

                    top_jobs['Final Score'] = final_scores[top_indices]

                    # Apply button
                    def make_apply_button(link):
                        return f'<a href="{link}" target="_blank"><button style="background:#1e40af; color:white; padding:10px 20px; border:none; border-radius:8px;">Apply Now</button></a>'

                    top_jobs['Apply'] = top_jobs['Links'].apply(make_apply_button)
                    top_jobs = top_jobs.drop(columns=['Links'])

                    top_jobs.index = [f"#{i+1}" for i in range(len(top_jobs))]

                    st.markdown("### Your Top 5 Perfect Jobs")
                    st.markdown(top_jobs.to_html(escape=False), unsafe_allow_html=True)
                    st.balloons()

                else:
                    st.warning("Please upload a valid resume.")
                

    # === MORE OPTIONS ===
    elif choice == "More":
        st.markdown("<h1 style='color: #1e40af; text-align: center;'>More Options</h1>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = 'login'
                st.success("Logged out successfully!")
                st.rerun()

        with col2:
            if st.button("Delete Account", use_container_width=True):
                delete_account(st.session_state.user['id'])
                st.session_state.user = None
                st.session_state.page = 'login'
                st.success("Account deleted.")
                st.rerun()


