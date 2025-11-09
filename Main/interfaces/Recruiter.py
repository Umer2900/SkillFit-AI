# # interfaces/Recruiter.py
# import streamlit as st
# import PyPDF2
# import io
# import time
# import pandas as pd
# import csv

# import zipfile
# import re
# from datetime import datetime
# from io import BytesIO

# from database import delete_account

# from Gemini_services.services import (
#     parse_job_description, parse_resume_for_recruiter,
#     compare_job_and_resume, feedback_parse
# )

# # ----------------------------------------------------------------------
# # Helpers
# # ----------------------------------------------------------------------
# def pdf_to_text(pdf_file) -> str:
#     reader = PyPDF2.PdfReader(pdf_file)
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text() or ""
#     return text

# def txt_to_text(txt_file) -> str:
#     return txt_file.read().decode("utf-8")

# # ----------------------------------------------------------------------
# # BULK SCREENING
# # ----------------------------------------------------------------------
# def screen_bulk_resumes_with_jd(zip_bytes: bytes, job_description: str, user_id: int):
#     start_time = time.time()
#     summary = []
#     filtered_files = {}
#     job_desc_parsed = parse_job_description(job_description)

#     with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_ref:
#         file_list = [
#             name for name in zip_ref.namelist()
#             if not name.startswith("__") and not name.endswith("/") and name.lower().endswith(('.pdf', '.txt'))
#         ]
#         total_files = len(file_list)
#         if total_files == 0:
#             st.warning("No PDF/TXT files found in the ZIP.")
#             return io.BytesIO().getvalue(), []

#         progress_bar = st.progress(0)
#         status_text = st.empty()

#         for idx, file_name in enumerate(file_list):
#             status_text.text(f"Processing: {file_name} ({idx+1}/{total_files})")

#             with zip_ref.open(file_name) as f:
#                 file_bytes = f.read()
#                 file_obj = io.BytesIO(file_bytes)

#                 try:
#                     resume_text = pdf_to_text(file_obj) if file_name.lower().endswith(".pdf") else txt_to_text(file_obj)
#                 except Exception:
#                     summary.append({"filename": file_name, "rating": "Error", "status": "Failed"})
#                     continue

#                 try:
#                     resume_parsed = parse_resume_for_recruiter(resume_text)
#                 except Exception:
#                     summary.append({"filename": file_name, "rating": "Error", "status": "Failed"})
#                     continue

#                 try:
#                     comparison = compare_job_and_resume(job_desc_parsed, resume_parsed)
#                 except Exception:
#                     summary.append({"filename": file_name, "rating": "Error", "status": "Failed"})
#                     continue

#                 rating_match = re.search(r"Rating:\s*(\d+)/10", comparison)
#                 rating = int(rating_match.group(1)) if rating_match else None
#                 status = "Passed" if rating and rating >= 7 else "Rejected"

#                 summary.append({
#                     "filename": file_name,
#                     "rating": f"{rating}/10" if rating else "N/A",
#                     "status": status
#                 })

#                 if status == "Passed":
#                     filtered_files[file_name] = file_bytes

#             progress_bar.progress((idx + 1) / total_files)

#         status_text.empty()
#         progress_bar.empty()

#     filtered_zip = io.BytesIO()
#     with zipfile.ZipFile(filtered_zip, "w", zipfile.ZIP_DEFLATED) as out_zip:
#         for name, data in filtered_files.items():
#             out_zip.writestr(name, data)
#     filtered_zip.seek(0)
#     st.caption(f"Completed in {time.time() - start_time:.1f} seconds")
#     return filtered_zip.getvalue(), summary

# # ----------------------------------------------------------------------
# # Main UI – CLEAN & FOCUSED
# # ----------------------------------------------------------------------
# def recruiter_interface():
#     st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
#     menu = ["Homepage", "Bulk Resume Screening","Profile Check", "More"]
#     choice = st.sidebar.selectbox("Menu", menu)

#     # HOMEPAGE
#     if choice == "Homepage":
#         st.title("Recruiter Homepage")
#         # st.subheader(f"Welcome to SkillFit AI, {st.session_state.user['username']}!")
#         st.markdown("""
#         ### Welcome to SkillFit AI — The Smartest Way to Hire

#         **No saved resumes. No clutter. No wasted time.**  
#         Just **instant, accurate, AI-powered candidate screening** — built for recruiters who value speed and precision.


#         #### What You Can Do Right Now

#         **1. Profile Check**  
#         Upload **one resume + one job description** → Get a crystal-clear match score (e.g., **9/10**) with detailed AI feedback in seconds.  
#         Perfect for quick shortlisting or validating a referral.

#         **2. Bulk Resume Screening**  
#         Drop a **ZIP with 50, 100, or 500 resumes** → Sit back.  
#         In under few minutes, download a clean ZIP + CSV containing **only the candidates who scored 7/10 or higher**.  
#         The rest? Gone. Forever.

#         **3. Zero Maintenance**  
#         - No "Liked" folders to manage  
#         - No database filling up  
#         - No duplicates, no mess  
#         - Just results → action → hire


#         #### Why Recruiters Love SkillFit AI

#         - **Saves 10+ hours per role** — no more manual reading  
#         - **Eliminates bias** — every resume judged purely on skills & experience  
#         - **100% private** — resumes never stored, never shared  
#         - **Export-ready** — ZIP for ATS, CSV for Excel/Google Sheets  
#         - **Powered by Google Gemini** — enterprise-grade AI, zero fluff


#         **You're one click away from hiring smarter.**

#         Use the sidebar → Pick **Profile Check** or **Bulk Screening** → Watch the magic happen.

#         **You focus on people. Let SkillFit AI handle the paper.**

#         **Ready to hire faster than ever?**  
#         Let's go
#         """)

#     # PROFILE CHECK 
#     elif choice == "Profile Check":
#         st.title("Profile Check")
#         st.write("Upload a resume and job description to see fit score.")

#         if "job_description" not in st.session_state:
#             st.session_state.job_description = ""
#         job_description = st.text_area(
#             "Enter Job Description", height=150,
#             value=st.session_state.job_description,
#             placeholder="Skills, Experience, Role..."
#         )

#         if "uploader_key" not in st.session_state:
#             st.session_state.uploader_key = 0
#         resume_file = st.file_uploader(
#             "Upload Resume (PDF/TXT)", type=["pdf", "txt"],
#             key=f"resume_uploader_{st.session_state.uploader_key}"
#         )

#         if "analysis_results" not in st.session_state:
#             st.session_state.analysis_results = {"job_desc": None, "resume": None, "comparison": None, "feedback": None}

#         if st.button("Analyze"):
#             if not job_description.strip():
#                 st.error("Enter a job description.")
#             elif not resume_file:
#                 st.error("Upload a resume.")
#             else:
#                 st.session_state.job_description = job_description
#                 resume_text = pdf_to_text(resume_file) if resume_file.type == "application/pdf" else txt_to_text(resume_file)

#                 if resume_text:
#                     with st.spinner("Analyzing..."):
#                         job_desc_text = parse_job_description(job_description)
#                         resume_parsed = parse_resume_for_recruiter(resume_text)
#                         comparison = compare_job_and_resume(job_desc_text, resume_parsed)
#                         feedback = feedback_parse(job_desc_text, resume_parsed)

#                     st.session_state.analysis_results = {
#                         "job_desc": job_desc_text,
#                         "resume": resume_parsed,
#                         "comparison": comparison,
#                         "feedback": feedback
#                     }

#         if st.session_state.analysis_results["job_desc"]:
#             cols = st.columns(4)
#             sections = ["job_desc", "resume", "comparison", "feedback"]
#             labels = ["Job Description", "Resume", "Comparison", "Feedback"]
#             for col, sec, label in zip(cols, sections, labels):
#                 with col:
#                     if st.button(label):
#                         st.session_state.selected_section = sec

#             if "selected_section" in st.session_state:
#                 st.write("---")
#                 sel = st.session_state.selected_section
#                 content = st.session_state.analysis_results[sel]
#                 if sel in ["job_desc", "resume"]:
#                     st.text(content)
#                 else:
#                     st.write(content)

#             if st.button("Clear"):
#                 # st.session_state.job_description = ""
#                 st.session_state.analysis_results = {"job_desc": None, "resume": None, "comparison": None, "feedback": None}
#                 st.session_state.uploader_key += 1
#                 st.rerun()

#     # BULK RESUME SCREENING – UNCHANGED & PERFECT
#     elif choice == "Bulk Resume Screening":
#         st.title("Bulk Resume Screening")
#         st.write("Upload a **job description** and a **ZIP of resumes**. Get only the best (≥ 7/10).")

#         if "bulk_job_description" not in st.session_state:
#             st.session_state.bulk_job_description = ""
#         if "bulk_zip_file" not in st.session_state:
#             st.session_state.bulk_zip_file = None
#         if "bulk_results" not in st.session_state:
#             st.session_state.bulk_results = None

#         job_description = st.text_area(
#             "Enter Job Description (required)", height=150,
#             value=st.session_state.bulk_job_description,
#             placeholder="Paste full JD here...",
#             key="bulk_jd_input"
#         )

#         zip_file = st.file_uploader("Upload ZIP of Resumes (PDF/TXT)", type=["zip"], key="bulk_zip_uploader")
#         if zip_file:
#             st.session_state.bulk_zip_file = zip_file

#         if st.button("Start Screening", type="primary", key="start_bulk"):
#             if not job_description.strip():
#                 st.error("Job description required.")
#             elif not zip_file:
#                 st.error("ZIP file required.")
#             else:
#                 st.session_state.bulk_job_description = job_description
#                 with st.spinner("Screening resumes..."):
#                     filtered_zip, summary = screen_bulk_resumes_with_jd(
#                         zip_file.read(), job_description, st.session_state.user['id']
#                     )
#                 st.session_state.bulk_results = {"filtered_zip": filtered_zip, "summary": summary}
#                 st.success("Done!")

#         if st.session_state.bulk_results:
#             st.markdown("---")
#             st.subheader("Screening Results")
#             df = pd.DataFrame([
#                 {"File": s["filename"], "Rating": s["rating"], "Status": s["status"]}
#                 for s in st.session_state.bulk_results["summary"]
#             ])
#             st.dataframe(df, use_container_width=True)

#             passed = df["Status"].eq("Passed").sum()
#             if passed > 0:
#                 st.success(f"**{passed} resume(s)** passed (≥ 7/10)")

#                 st.download_button(
#                     label="Download Filtered ZIP",
#                     data=st.session_state.bulk_results["filtered_zip"],
#                     file_name="filtered_top_resumes.zip",
#                     mime="application/zip",
#                     key="dl_zip"
#                 )

#                 csv_buffer = io.StringIO()
#                 writer = csv.writer(csv_buffer)
#                 writer.writerow(["File", "Rating", "Status"])
#                 for s in st.session_state.bulk_results["summary"]:
#                     writer.writerow([s["filename"], f'="{s["rating"]}"', s["status"]])
#                 st.download_button(
#                     label="Download CSV",
#                     data=csv_buffer.getvalue(),
#                     file_name="screening_results.csv",
#                     mime="text/csv",
#                     key="dl_csv"
#                 )
#             else:
#                 st.warning("No resumes passed.")

#             st.markdown("---")
#             if st.button("Clear", type="secondary", key="clear_bulk"):
#                 # st.session_state.bulk_job_description = ""
#                 st.session_state.bulk_zip_file = None
#                 st.session_state.bulk_results = None
#                 st.rerun()

#     # MORE
#     elif choice == "More":
#         st.title("More Options")
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("Logout"):
#                 st.session_state.user = None
#                 st.session_state.page = 'login'
#                 st.rerun()
#         with col2:
#             if st.button("Delete Account"):
#                 delete_account(st.session_state.user['id'])
#                 st.session_state.user = None
#                 st.session_state.page = 'login'
#                 st.success("Account deleted.")
#                 st.rerun()





# interfaces/Recruiter.py - FINAL: BEAUTIFUL RECRUITER UI
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
# BULK SCREENING (UNCHANGED)
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
# RECRUITER INTERFACE — BEAUTIFUL & PROFESSIONAL
# ----------------------------------------------------------------------
def recruiter_interface():
    # === SIDEBAR: SKILLFIT AI + USERNAME IN BLUE ===
    st.sidebar.markdown("""
    <h1 style='color: #1e40af; font-size: 28px; font-weight: 900; margin-bottom: 5px;'>
        SkillFit AI
    </h1>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <p style='color: #1e40af; font-size: 20px; font-weight: bold; margin-top: 0;'>
        Welcome, {st.session_state.user['username']}!
    </p>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    menu = ["Homepage", "Bulk Resume Screening", "Profile Check", "More"]
    choice = st.sidebar.selectbox("Menu", menu, label_visibility="collapsed")

    # === HOMEPAGE — REDESIGNED & POWERFUL ===
    if choice == "Homepage":
        st.markdown("""
        <h1 style='text-align: center; color: #1e40af; font-size: 48px; font-weight: 900;'>
            SkillFit AI
        </h1>
        <p style='text-align: center; color: #555; font-size: 22px; margin-bottom: 40px;'>
            <strong>AI-Powered Hiring.</strong> Zero Clutter. Pure Results.
        </p>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); padding: 30px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);">
            <h2 style="color: #1e40af; margin-top: 0;">
                Welcome, <span style="color: #1e3a8a; font-weight: 900;">{username}</span>!
            </h2>
            <p style="font-size: 18px; color: #1e40af;">
                You're one click away from hiring <strong>10x faster</strong>.
            </p>
        </div>
        """.format(username=st.session_state.user['username']), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background: #f0f9ff; padding: 25px; border-radius: 14px; border-left: 6px solid #0ea5e9; height: 100%;">
                <h3 style="color: #0c4a6b;">Profile Check</h3>
                <p>Upload <strong>1 resume + 1 JD</strong> → Get instant 10/10 score + AI feedback.</p>
                <p><strong>Perfect for:</strong> referrals, quick validation</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="background: #fef3c7; padding: 25px; border-radius: 14px; border-left: 6px solid #f59e0b; height: 100%;">
                <h3 style="color: #92400e;">Bulk Screening</h3>
                <p>Drop a <strong>ZIP of 500 resumes</strong> → Get only the top 7+/10 in seconds.</p>
                <p><strong>Perfect for:</strong> high-volume roles, campus hiring</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #ecfdf5; padding: 25px; border-radius: 14px; border: 2px dashed #10b981; text-align: center;">
            <h3 style="color: #065f46; margin-top: 0;">Why SkillFit AI Works</h3>
            <p style="font-size: 18px;">
                • <strong>No saved resumes</strong> → Zero clutter<br>
                • <strong>100% private</strong> → Resumes deleted instantly<br>
                • <strong>Export-ready</strong> → ZIP + CSV for ATS/Excel<br>
                • <strong>Powered by Gemini Pro</strong> → Enterprise-grade AI
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <p style="text-align: center; font-size: 20px; color: #1e40af;">
            <strong>Ready to hire smarter?</strong><br>
            Use the sidebar → Pick your tool → <strong>Watch the magic.</strong>
        </p>
        """, unsafe_allow_html=True)


    # === PROFILE CHECK — ALL OUTPUTS NOW IN CLEAN TEXT ===
    elif choice == "Profile Check":
        st.markdown("<h1 style='color: #1e40af; text-align: center;'>Profile Check</h1>", unsafe_allow_html=True)
        st.write("Upload a resume + job description → Get instant AI-powered match score.")

        if "job_description" not in st.session_state:
            st.session_state.job_description = ""
        job_description = st.text_area(
            "Enter Job Description", height=150,
            value=st.session_state.job_description,
            placeholder="Paste full JD here..."
        )

        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0
        resume_file = st.file_uploader(
            "Upload Resume (PDF/TXT)", type=["pdf", "txt"],
            key=f"resume_uploader_{st.session_state.uploader_key}"
        )

        if "analysis_results" not in st.session_state:
            st.session_state.analysis_results = {"job_desc": None, "resume": None, "comparison": None, "feedback": None}

        if st.button("Analyze Resume", use_container_width=True, type="primary"):
            if not job_description.strip():
                st.error("Job description required.")
            elif not resume_file:
                st.error("Resume required.")
            else:
                st.session_state.job_description = job_description
                resume_text = pdf_to_text(resume_file) if resume_file.type == "application/pdf" else txt_to_text(resume_file)

                if resume_text.strip():
                    with st.spinner("AI is analyzing..."):
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
                    st.success("Analysis complete!")

        if st.session_state.analysis_results["job_desc"]:
            cols = st.columns(4)
            sections = ["job_desc", "resume", "comparison", "feedback"]
            labels = ["Job Description", "Resume", "Comparison", "Feedback"]
            for col, sec, label in zip(cols, sections, labels):
                with col:
                    if st.button(label, use_container_width=True):
                        st.session_state.selected_section = sec

            if "selected_section" in st.session_state:
                st.markdown("---")
                sel = st.session_state.selected_section
                content = st.session_state.analysis_results[sel]

                # ALL NOW DISPLAYED AS CLEAN, NON-COPYABLE TEXT
                if sel == "job_desc":
                    st.markdown("### Parsed Job Description")
                    st.write(content)
                elif sel == "resume":
                    st.markdown("### Parsed Resume")
                    st.write(content)
                elif sel == "comparison":
                    st.markdown("### AI Comparison & Match Score")
                    st.write(content)
                elif sel == "feedback":
                    st.markdown("### AI Feedback & Recommendations")
                    st.write(content)

            if st.button("Clear All", use_container_width=True, type="secondary"):
                st.session_state.analysis_results = {"job_desc": None, "resume": None, "comparison": None, "feedback": None}
                st.session_state.uploader_key += 1
                st.rerun()



    # === BULK SCREENING (UNCHANGED LOGIC, BETTER UI) ===
    elif choice == "Bulk Resume Screening":
        st.markdown("<h1 style='color: #1e40af; text-align: center;'>Bulk Resume Screening</h1>", unsafe_allow_html=True)
        st.write("Upload a **ZIP of resumes** + JD → Download only the **top 7+/10 candidates**.")

        job_description = st.text_area(
            "Enter Job Description (required)", height=150,
            placeholder="Paste full JD here..."
        )

        zip_file = st.file_uploader("Upload ZIP of Resumes (PDF/TXT)", type=["zip"])

        if st.button("Start Screening", use_container_width=True, type="primary"):
            if not job_description.strip():
                st.error("Job description required.")
            elif not zip_file:
                st.error("ZIP file required.")
            else:
                with st.spinner("Screening resumes..."):
                    filtered_zip, summary = screen_bulk_resumes_with_jd(
                        zip_file.read(), job_description, st.session_state.user['id']
                    )
                st.session_state.bulk_results = {"filtered_zip": filtered_zip, "summary": summary}
                st.success("Screening complete!")

        if "bulk_results" in st.session_state and st.session_state.bulk_results:
            st.markdown("---")
            st.subheader("Results")
            df = pd.DataFrame([
                {"File": s["filename"], "Rating": s["rating"], "Status": s["status"]}
                for s in st.session_state.bulk_results["summary"]
            ])
            st.dataframe(df, use_container_width=True)

            passed = df["Status"].eq("Passed").sum()
            if passed > 0:
                st.success(f"**{passed} candidate(s)** passed!")
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download Filtered ZIP",
                        data=st.session_state.bulk_results["filtered_zip"],
                        file_name="top_candidates.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                with col2:
                    csv_buffer = io.StringIO()
                    writer = csv.writer(csv_buffer)
                    writer.writerow(["File", "Rating", "Status"])
                    for s in st.session_state.bulk_results["summary"]:
                        writer.writerow([s["filename"], f'="{s["rating"]}"', s["status"]])
                    st.download_button(
                        "Download CSV Report",
                        data=csv_buffer.getvalue(),
                        file_name="screening_report.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.warning("No resumes passed the 7/10 threshold.")

            if st.button("Clear Results", use_container_width=True, type="secondary"):
                st.session_state.bulk_results = None
                st.rerun()

    # === MORE ===
    elif choice == "More":
        st.markdown("<h1 style='color: #1e40af; text-align: center;'>More Options</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = 'login'
                st.rerun()
        with col2:
            if st.button("Delete Account", use_container_width=True, type="secondary"):
                delete_account(st.session_state.user['id'])
                st.session_state.user = None
                st.session_state.page = 'login'
                st.success("Account deleted.")
                st.rerun()