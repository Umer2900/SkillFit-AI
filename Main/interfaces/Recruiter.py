# interfaces/Recruiter.py
import streamlit as st
import PyPDF2
import io
import time
import pandas as pd
import csv

import zipfile
import re
from datetime import datetime
from io import BytesIO

# Removed: save_resume, get_user_resumes, clear_resumes
from database import delete_account

from Gemini_services.services import (
    parse_job_description, parse_resume_for_recruiter,
    compare_job_and_resume, feedback_parse
)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def pdf_to_text(pdf_file) -> str:
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def txt_to_text(txt_file) -> str:
    return txt_file.read().decode("utf-8")

# ----------------------------------------------------------------------
# BULK SCREENING
# ----------------------------------------------------------------------
def screen_bulk_resumes_with_jd(zip_bytes: bytes, job_description: str, user_id: int):
    start_time = time.time()
    summary = []
    filtered_files = {}
    job_desc_parsed = parse_job_description(job_description)

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_ref:
        file_list = [
            name for name in zip_ref.namelist()
            if not name.startswith("__") and not name.endswith("/") and name.lower().endswith(('.pdf', '.txt'))
        ]
        total_files = len(file_list)
        if total_files == 0:
            st.warning("No PDF/TXT files found in the ZIP.")
            return io.BytesIO().getvalue(), []

        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, file_name in enumerate(file_list):
            status_text.text(f"Processing: {file_name} ({idx+1}/{total_files})")

            with zip_ref.open(file_name) as f:
                file_bytes = f.read()
                file_obj = io.BytesIO(file_bytes)

                try:
                    resume_text = pdf_to_text(file_obj) if file_name.lower().endswith(".pdf") else txt_to_text(file_obj)
                except Exception:
                    summary.append({"filename": file_name, "rating": "Error", "status": "Failed"})
                    continue

                try:
                    resume_parsed = parse_resume_for_recruiter(resume_text)
                except Exception:
                    summary.append({"filename": file_name, "rating": "Error", "status": "Failed"})
                    continue

                try:
                    comparison = compare_job_and_resume(job_desc_parsed, resume_parsed)
                except Exception:
                    summary.append({"filename": file_name, "rating": "Error", "status": "Failed"})
                    continue

                rating_match = re.search(r"Rating:\s*(\d+)/10", comparison)
                rating = int(rating_match.group(1)) if rating_match else None
                status = "Passed" if rating and rating >= 7 else "Rejected"

                summary.append({
                    "filename": file_name,
                    "rating": f"{rating}/10" if rating else "N/A",
                    "status": status
                })

                if status == "Passed":
                    filtered_files[file_name] = file_bytes

            progress_bar.progress((idx + 1) / total_files)

        status_text.empty()
        progress_bar.empty()

    filtered_zip = io.BytesIO()
    with zipfile.ZipFile(filtered_zip, "w", zipfile.ZIP_DEFLATED) as out_zip:
        for name, data in filtered_files.items():
            out_zip.writestr(name, data)
    filtered_zip.seek(0)
    st.caption(f"Completed in {time.time() - start_time:.1f} seconds")
    return filtered_zip.getvalue(), summary

# ----------------------------------------------------------------------
# Main UI – CLEAN & FOCUSED
# ----------------------------------------------------------------------
def recruiter_interface():
    st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
    menu = ["Homepage", "Profile Check", "Bulk Resume Screening", "More"]
    choice = st.sidebar.selectbox("Menu", menu)

    # HOMEPAGE
    if choice == "Homepage":
        st.title("Recruiter Homepage")
        st.subheader(f"Welcome to SkillFit AI, {st.session_state.user['username']}!")
        st.markdown("""
        ### AI-Powered Recruitment — Simplified

        No more manual resume screening. No saved lists. Just **pure efficiency**.

        - **Profile Check**: Compare one resume to a job description instantly.
        - **Bulk Screening**: Upload 100 resumes → Get top 10 in seconds.
        - **Download ZIP + CSV**: Take results anywhere.

        **You focus on hiring. We handle the noise.**
        """)

    # PROFILE CHECK 
    elif choice == "Profile Check":
        st.title("Profile Check")
        st.write("Upload a resume and job description to see fit score.")

        if "job_description" not in st.session_state:
            st.session_state.job_description = ""
        job_description = st.text_area(
            "Enter Job Description", height=150,
            value=st.session_state.job_description,
            placeholder="Skills, Experience, Role..."
        )

        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0
        resume_file = st.file_uploader(
            "Upload Resume (PDF/TXT)", type=["pdf", "txt"],
            key=f"resume_uploader_{st.session_state.uploader_key}"
        )

        if "analysis_results" not in st.session_state:
            st.session_state.analysis_results = {"job_desc": None, "resume": None, "comparison": None, "feedback": None}

        if st.button("Analyze"):
            if not job_description.strip():
                st.error("Enter a job description.")
            elif not resume_file:
                st.error("Upload a resume.")
            else:
                st.session_state.job_description = job_description
                resume_text = pdf_to_text(resume_file) if resume_file.type == "application/pdf" else txt_to_text(resume_file)

                if resume_text:
                    with st.spinner("Analyzing..."):
                        job_desc_text = parse_job_description(job_description)
                        resume_parsed = parse_resume_for_recruiter(resume_text)
                        comparison = compare_job_and_resume(job_desc_text, resume_parsed)
                        feedback = feedback_parse(job_desc_text, resume_parsed)

                    st.session_state.analysis_results = {
                        "job_desc": job_desc_text,
                        "resume": resume_parsed,
                        "comparison": comparison,
                        "feedback": feedback
                    }

        if st.session_state.analysis_results["job_desc"]:
            cols = st.columns(4)
            sections = ["job_desc", "resume", "comparison", "feedback"]
            labels = ["Job Description", "Resume", "Comparison", "Feedback"]
            for col, sec, label in zip(cols, sections, labels):
                with col:
                    if st.button(label):
                        st.session_state.selected_section = sec

            if "selected_section" in st.session_state:
                st.write("---")
                sel = st.session_state.selected_section
                content = st.session_state.analysis_results[sel]
                if sel in ["job_desc", "resume"]:
                    st.text(content)
                else:
                    st.write(content)

            if st.button("Clear"):
                # st.session_state.job_description = ""
                st.session_state.analysis_results = {"job_desc": None, "resume": None, "comparison": None, "feedback": None}
                st.session_state.uploader_key += 1
                st.rerun()

    # BULK RESUME SCREENING – UNCHANGED & PERFECT
    elif choice == "Bulk Resume Screening":
        st.title("Bulk Resume Screening")
        st.write("Upload a **job description** and a **ZIP of resumes**. Get only the best (≥ 7/10).")

        if "bulk_job_description" not in st.session_state:
            st.session_state.bulk_job_description = ""
        if "bulk_zip_file" not in st.session_state:
            st.session_state.bulk_zip_file = None
        if "bulk_results" not in st.session_state:
            st.session_state.bulk_results = None

        job_description = st.text_area(
            "Enter Job Description (required)", height=150,
            value=st.session_state.bulk_job_description,
            placeholder="Paste full JD here...",
            key="bulk_jd_input"
        )

        zip_file = st.file_uploader("Upload ZIP of Resumes (PDF/TXT)", type=["zip"], key="bulk_zip_uploader")
        if zip_file:
            st.session_state.bulk_zip_file = zip_file

        if st.button("Start Screening", type="primary", key="start_bulk"):
            if not job_description.strip():
                st.error("Job description required.")
            elif not zip_file:
                st.error("ZIP file required.")
            else:
                st.session_state.bulk_job_description = job_description
                with st.spinner("Screening resumes..."):
                    filtered_zip, summary = screen_bulk_resumes_with_jd(
                        zip_file.read(), job_description, st.session_state.user['id']
                    )
                st.session_state.bulk_results = {"filtered_zip": filtered_zip, "summary": summary}
                st.success("Done!")

        if st.session_state.bulk_results:
            st.markdown("---")
            st.subheader("Screening Results")
            df = pd.DataFrame([
                {"File": s["filename"], "Rating": s["rating"], "Status": s["status"]}
                for s in st.session_state.bulk_results["summary"]
            ])
            st.dataframe(df, use_container_width=True)

            passed = df["Status"].eq("Passed").sum()
            if passed > 0:
                st.success(f"**{passed} resume(s)** passed (≥ 7/10)")

                st.download_button(
                    label="Download Filtered ZIP",
                    data=st.session_state.bulk_results["filtered_zip"],
                    file_name="filtered_top_resumes.zip",
                    mime="application/zip",
                    key="dl_zip"
                )

                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer)
                writer.writerow(["File", "Rating", "Status"])
                for s in st.session_state.bulk_results["summary"]:
                    writer.writerow([s["filename"], f'="{s["rating"]}"', s["status"]])
                st.download_button(
                    label="Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name="screening_results.csv",
                    mime="text/csv",
                    key="dl_csv"
                )
            else:
                st.warning("No resumes passed.")

            st.markdown("---")
            if st.button("Clear", type="secondary", key="clear_bulk"):
                # st.session_state.bulk_job_description = ""
                st.session_state.bulk_zip_file = None
                st.session_state.bulk_results = None
                st.rerun()

    # MORE
    elif choice == "More":
        st.title("More Options")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Logout"):
                st.session_state.user = None
                st.session_state.page = 'login'
                st.rerun()
        with col2:
            if st.button("Delete Account"):
                delete_account(st.session_state.user['id'])
                st.session_state.user = None
                st.session_state.page = 'login'
                st.success("Account deleted.")
                st.rerun()
