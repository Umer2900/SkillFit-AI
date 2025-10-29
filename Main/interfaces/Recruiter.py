# interfaces/Recruiter.py
import streamlit as st
import PyPDF2
import io
import time

import zipfile
import re
from tqdm import tqdm  # optional, only if you want fancy progress
from datetime import datetime
from io import BytesIO

from database import (
    save_resume, get_user_resumes, download_resume,
    clear_resumes, delete_account
)
from Gemini_services.services import (
    parse_job_description, parse_resume_for_recruiter,
    compare_job_and_resume, feedback_parse
)

# ----------------------------------------------------------------------
# Helper: PDF → plain text
# ----------------------------------------------------------------------
def pdf_to_text(pdf_file) -> str:
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ----------------------------------------------------------------------
# Helper: TXT → plain text
# ----------------------------------------------------------------------
def txt_to_text(txt_file) -> str:
    return txt_file.read().decode("utf-8")

# ----------------------------------------------------------------------
# BULK SCREENING WITH JOB DESCRIPTION
# ----------------------------------------------------------------------
def screen_bulk_resumes_with_jd(zip_bytes: bytes, job_description: str, user_id: int):
    """
    Returns:
        filtered_zip_bytes (bytes)
        summary (list of dicts): [{filename, rating, status}]
    """
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

                # Extract text
                try:
                    if file_name.lower().endswith(".pdf"):
                        resume_text = pdf_to_text(file_obj)
                    else:
                        resume_text = txt_to_text(file_obj)
                except Exception as e:
                    summary.append({"filename": file_name, "rating": "Error", "status": "Failed"})
                    continue

                # Parse resume
                try:
                    resume_parsed = parse_resume_for_recruiter(resume_text)
                except Exception as e:
                    summary.append({"filename": file_name, "rating": "Error", "status": "Failed"})
                    continue

                # Compare
                try:
                    comparison = compare_job_and_resume(job_desc_parsed, resume_parsed)
                except Exception as e:
                    summary.append({"filename": file_name, "rating": "Error", "status": "Failed"})
                    continue

                # Extract rating
                rating_match = re.search(r"Rating:\s*(\d+)/10", comparison)
                rating = int(rating_match.group(1)) if rating_match else None

                status = "Passed" if rating and rating >= 7 else "Rejected"
                summary.append({
                    "filename": file_name,
                    "rating": f"{rating}/10" if rating else "N/A",
                    "status": status
                })

                # Keep only if passed
                if status == "Passed":
                    filtered_files[file_name] = file_bytes

            progress_bar.progress((idx + 1) / total_files)

        status_text.empty()
        progress_bar.empty()

    # Build filtered ZIP
    filtered_zip = io.BytesIO()
    with zipfile.ZipFile(filtered_zip, "w", zipfile.ZIP_DEFLATED) as out_zip:
        for name, data in filtered_files.items():
            out_zip.writestr(name, data)
    filtered_zip.seek(0)
    elapsed = time.time() - start_time
    st.caption(f"Completed in {elapsed:.1f} seconds")
    return filtered_zip.getvalue(), summary

# ----------------------------------------------------------------------
# Main UI
# ----------------------------------------------------------------------
def recruiter_interface():
    st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
    menu = ["Homepage", "Profile Check", "Liked Resume", "Bulk Resume Screening", "More"]
    choice = st.sidebar.selectbox("Menu", menu)

    # ------------------------------------------------------------------
    # HOMEPAGE
    # ------------------------------------------------------------------
    if choice == "Homepage":
        st.title("Recruiter Homepage")
        st.subheader(f"Welcome to SkillFit AI, {st.session_state.user['username']}!")
        st.markdown(""" ... (your existing long text) ... """)

    # ------------------------------------------------------------------
    # PROFILE CHECK (unchanged – only the Save button was tweaked a bit)
    # ------------------------------------------------------------------
    elif choice == "Profile Check":
        st.title("Profile Check")
        st.write("Upload your resume and enter a job description to see how well you fit the job.")

        if "job_description" not in st.session_state:
            st.session_state.job_description = ""
        job_description = st.text_area(
            "Enter Job Description", height=150,
            value=st.session_state.job_description,
            placeholder="At least mention the Skills, Experience and JobRole"
        )

        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0
        if "resume_file" not in st.session_state:
            st.session_state.resume_file = None
        if "resume_filename" not in st.session_state:
            st.session_state.resume_filename = None

        resume_file = st.file_uploader(
            "Upload Resume (PDF or TXT)", type=["pdf", "txt"],
            key=f"resume_uploader_{st.session_state.uploader_key}"
        )
        if resume_file:
            st.session_state.resume_file = resume_file
            st.session_state.resume_filename = resume_file.name

        if "analysis_results" not in st.session_state:
            st.session_state.analysis_results = {
                "job_desc": None, "resume": None,
                "comparison": None, "feedback": None
            }

        st.write(" ")
        if st.button("Analyze"):
            if not job_description:
                st.error("Please enter a job description.")
            elif not resume_file:
                st.error("Please upload your resume.")
            else:
                st.session_state.job_description = job_description
                st.session_state.resume_file = resume_file

                file_type = resume_file.type
                resume_text = ""
                if file_type == "application/pdf":
                    st.write("Processing PDF…")
                    resume_text = pdf_to_text(resume_file)
                elif file_type == "text/plain":
                    st.write("Processing TXT…")
                    resume_text = txt_to_text(resume_file)
                else:
                    st.error("Unsupported file format.")
                    resume_text = ""

                if resume_text:
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

        # ---- display analysis ------------------------------------------------
        if st.session_state.analysis_results["job_desc"] is not None:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Job Description"):
                    st.session_state.selected_section = "job_desc"
            with col2:
                if st.button("Resume"):
                    st.session_state.selected_section = "resume"
            with col3:
                if st.button("Comparison"):
                    st.session_state.selected_section = "comparison"
            with col4:
                if st.button("Feedback"):
                    st.session_state.selected_section = "feedback"

            if "selected_section" in st.session_state:
                st.write("---")
                sel = st.session_state.selected_section
                if sel == "job_desc":
                    st.text(st.session_state.analysis_results["job_desc"])
                elif sel == "resume":
                    st.text(st.session_state.analysis_results["resume"])
                elif sel == "comparison":
                    st.write(st.session_state.analysis_results["comparison"])
                elif sel == "feedback":
                    st.write(st.session_state.analysis_results["feedback"])

            # ---- Clear / Save ------------------------------------------------
            col5, col6 = st.columns(2)
            with col5:
                if st.button("Clear"):
                    st.session_state.job_description = ""
                    st.session_state.resume_file = None
                    st.session_state.analysis_results = {"job_desc": None, "resume": None,
                                                       "comparison": None, "feedback": None}
                    st.session_state.uploader_key += 1
                    st.rerun()
            with col6:
                if st.button("Save"):
                    if st.session_state.resume_file:
                        resumes = get_user_resumes(st.session_state.user['id'])
                        if resumes and any(r[1] == st.session_state.resume_filename for r in resumes):
                            st.warning("It's already Liked.")
                        else:
                            try:
                                save_resume(st.session_state.user['id'], st.session_state.resume_file)
                                st.success(f"Resume '{st.session_state.resume_filename}' saved.")
                                st.session_state.resume_file = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to save resume: {e}")
                    else:
                        st.error("No resume uploaded to save.")

    # ------------------------------------------------------------------
    # LIKED RESUME (unchanged)
    # ------------------------------------------------------------------
    elif choice == "Liked Resume":
        st.title("Liked Resume")
        resumes = get_user_resumes(st.session_state.user['id'])
        if resumes:
            for resume in resumes:
                content = resume[3]                     # file_content
                upload_date = datetime.strptime(resume[2], "%Y-%m-%d %H:%M:%S.%f")
                formatted_date = upload_date.strftime("%Y-%m-%d at %I:%M %p")
                st.subheader(resume[1])                # filename
                st.write(f"Saved on: {formatted_date}")
                st.download_button(
                    label="Download Resume",
                    data=BytesIO(content),
                    file_name=resume[1]
                )
                if resume[4]:
                    st.write("Analysis:", resume[4])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear"):
                    clear_resumes(st.session_state.user['id'])
                    st.success("All liked resumes cleared!")
                    st.rerun()
        else:
            st.write("No resumes saved yet.")

    # ------------------------------------------------------------------
    # NEW: BULK RESUME SCREENING
    # ------------------------------------------------------------------
    elif choice == "Bulk Resume Screening":
        st.title("Bulk Resume Screening")
        st.write(
            "Upload a **job description** and a **ZIP of resumes**. "
            "The AI will evaluate each resume and return only those scoring **≥ 7/10**."
        )

        # === Initialize Session State ===
        if "bulk_job_description" not in st.session_state:
            st.session_state.bulk_job_description = ""
        if "bulk_zip_file" not in st.session_state:
            st.session_state.bulk_zip_file = None
        if "bulk_results" not in st.session_state:
            st.session_state.bulk_results = None

        # === Input Section ===
        job_description = st.text_area(
            "Enter Job Description (required)",
            height=150,
            value=st.session_state.bulk_job_description,
            placeholder="Paste the full job description here...",
            key="bulk_jd_input"
        )

        zip_file = st.file_uploader(
            "Upload ZIP of Resumes (PDF/TXT)",
            type=["zip"],
            key="bulk_zip_uploader"
        )
        if zip_file is not None:
            st.session_state.bulk_zip_file = zip_file

        # === Start Button (Only) ===
        if st.button("Start Screening", type="primary", key="start_bulk"):
            if not job_description.strip():
                st.error("Please enter a job description.")
            elif not zip_file:
                st.error("Please upload a ZIP file.")
            else:
                st.session_state.bulk_job_description = job_description
                zip_bytes = zip_file.read()

                with st.spinner("Screening resumes..."):
                    filtered_zip, summary = screen_bulk_resumes_with_jd(
                        zip_bytes, job_description, st.session_state.user['id']
                    )
                st.session_state.bulk_results = {
                    "filtered_zip": filtered_zip,
                    "summary": summary
                }
                st.success("Screening complete!")

        # === RESULTS SECTION – ONLY SHOW AFTER SCREENING ===
        if st.session_state.bulk_results:
            st.markdown("---")
            st.subheader("Screening Results")

            # Table
            results = [
                {"File": s["filename"], "Rating": s["rating"], "Status": s["status"]}
                for s in st.session_state.bulk_results["summary"]
            ]
            st.dataframe(results, use_container_width=True)

            # Stats + Download
            passed_count = len([s for s in results if s["Status"] == "Passed"])
            if passed_count > 0:
                st.success(f"**{passed_count} resume(s)** passed (≥ 7/10)")
                st.download_button(
                    label=f"Download {passed_count} Filtered Resume(s)",
                    data=st.session_state.bulk_results["filtered_zip"],
                    file_name="filtered_top_resumes.zip",
                    mime="application/zip",
                    key="download_filtered_bulk"
                )
            else:
                st.warning("No resumes met the ≥ 7/10 threshold.")

            # === CLEAR BUTTON – AT THE VERY END ===
            st.markdown("---")
            # col_left, col_right = st.columns([5, 1])
            # with col_right:
            #     if st.button("Clear", type="secondary", key="clear_results_final"):
            #         # Reset ALL session state
            #         st.session_state.bulk_job_description = ""
            #         st.session_state.bulk_zip_file = None
            #         st.session_state.bulk_results = None
            #         st.rerun()
            
            col_right, = st.columns(1)  # note the comma to unpack the single element
            with col_right:
                if st.button("Clear"):
                    st.session_state.bulk_job_description = ""
                    st.session_state.bulk_zip_file = None
                    st.session_state.bulk_results = None
                    st.rerun()


    # elif choice == "Bulk Resume Screening":
    #     st.title("Bulk Resume Screening")
    #     st.write(
    #         "Upload a **job description** and a **ZIP of resumes**. "
    #         "The AI will evaluate each resume against the job and return only those scoring **≥ 7/10**."
    #     )

    #     # --- Job Description Input ---
    #     if "bulk_job_description" not in st.session_state:
    #         st.session_state.bulk_job_description = ""
    #     job_description = st.text_area(
    #         "Enter Job Description (required)",
    #         height=150,
    #         value=st.session_state.bulk_job_description,
    #         placeholder="Paste the full job description here (skills, experience, role, etc.)",
    #         key="bulk_jd_input"
    #     )

    #     # --- ZIP Upload ---
    #     zip_file = st.file_uploader(
    #         "Upload ZIP of Resumes (PDF/TXT)",
    #         type=["zip"],
    #         key="bulk_zip_uploader"
    #     )

    #     # --- Single Start Button ---
    #     if st.button("Start Screening", type="primary"):
    #         if not job_description.strip():
    #             st.error("Please enter a job description.")
    #         elif not zip_file:
    #             st.error("Please upload a ZIP file containing resumes.")
    #         else:
    #             # Save to session for persistence
    #             st.session_state.bulk_job_description = job_description
    #             zip_bytes = zip_file.read()

    #             with st.spinner("Screening resumes against the job description..."):
    #                 filtered_zip, summary = screen_bulk_resumes_with_jd(
    #                     zip_bytes, job_description, st.session_state.user['id']
    #                 )

    #             # --- Summary Table ---
    #             st.subheader("Screening Results")
    #             results = [
    #                 {"File": s["filename"], "Rating": s["rating"], "Status": s["status"]}
    #                 for s in summary
    #             ]
    #             st.dataframe(results, use_container_width=True)

    #             # --- Download Filtered ZIP ---
    #             passed_count = len([s for s in summary if s["status"] == "Passed"])
    #             if passed_count > 0:
    #                 st.success(f"{passed_count} resume(s) passed (≥ 7/10). Download below.")
    #                 st.download_button(
    #                     label=f"Download {passed_count} Filtered Resume(s)",
    #                     data=filtered_zip,
    #                     file_name="filtered_top_resumes.zip",
    #                     mime="application/zip",
    #                     key="download_filtered"
    #                 )
    #             else:
    #                 st.warning("No resumes met the ≥ 7/10 threshold.")

    # ------------------------------------------------------------------
    # MORE (logout / delete)
    # ------------------------------------------------------------------
    elif choice == "More":
        st.title("More Options")
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













##########################################################################################################################
# Second One: After Supabase  --> but before Bulk Resume 

# import streamlit as st
# import PyPDF2
# from database import save_resume, get_user_resumes, download_resume, clear_resumes, delete_account
# from datetime import datetime
# from io import BytesIO
# from Gemini_services.services import parse_job_description, parse_resume_for_recruiter, compare_job_and_resume, feedback_parse

# # Helper function to extract text from a PDF
# def pdf_to_text(pdf_file):
#     reader = PyPDF2.PdfReader(pdf_file)
#     text = ""
#     for page_num in range(len(reader.pages)):
#         page = reader.pages[page_num]
#         text += page.extract_text()
#     return text

# # Helper function to extract text from a TXT file
# def txt_to_text(txt_file):
#     return txt_file.read().decode("utf-8")

# # Streamlit UI for Recruiter
# def recruiter_interface():
#     st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
#     menu = ["Homepage", "Profile Check", "Liked Resume", "More"]
#     choice = st.sidebar.selectbox("Menu", menu)
    
#     if choice == "Homepage":
#         st.title("Recruiter Homepage")
#         st.subheader(f"Welcome to SkillFit AI, {st.session_state.user['username']}!")
#         st.markdown("""
#         ### Unlock the Power of AI-Driven Recruitment

#         As a recruiter, you’re here to find the best talent for your organization, and **SkillFit AI** is designed to make that process smarter, faster, and more efficient. Powered by the Gemini API, our platform offers cutting-edge tools to help you evaluate candidates with precision and ease. Whether you're analyzing resumes, comparing them against job descriptions, or managing your favorite candidates, we’ve got you covered.

#         #### What You Can Do Here

#         **SkillFit AI** provides a tailored experience for recruiters through three key sections accessible from the sidebar:

#         1. **Profile Check**  
#            - **What It Does**: Upload a job description and a candidate’s resume to get a detailed analysis. Our AI extracts key details like job roles, experience, and skills from both documents, compares them, and provides a compatibility rating along with actionable feedback.  
#            - **Why It’s Useful**: Quickly identify if a candidate is a good fit for the role without manually sifting through documents. The AI-driven comparison ensures you focus on the most relevant candidates, saving you time and effort.  
#            - **How to Use It**: Navigate to “Profile Check,” upload a job description (TXT) and a resume (PDF or TXT), and click “Analyze” to see the results. You can also save promising resumes for later review.

#         2. **Liked Resume**  
#            - **What It Does**: View and manage all the resumes you’ve saved from the “Profile Check” section. Download resumes, review their details, or clear the list if needed.  
#            - **Why It’s Useful**: Keep track of top candidates in one place. This section acts as your personal shortlist, making it easy to revisit and compare your favorite profiles.  
#            - **How to Use It**: Go to “Liked Resume” to see your saved resumes. Use the “Download” button to retrieve a resume or the “Clear” button to remove all saved resumes.

#         3. **More Options**  
#            - **What It Does**: Access additional account management features, such as logging out or deleting your account.  
#            - **Why It’s Useful**: Securely manage your account with ease. If you’re done for the day, log out to keep your session safe. Need to remove your account? The “Delete Account” option ensures all your data (including saved resumes) is permanently deleted.  
#            - **How to Use It**: Navigate to “More,” then choose “Logout” to end your session or “Delete Account” to remove your profile.

#         #### Why Choose SkillFit AI?
#         - **AI-Powered Insights**: Leverage the Gemini API to parse and analyze documents with unparalleled accuracy.  
#         - **Time-Saving**: Automate the tedious parts of recruitment, so you can focus on what matters—building great teams.  
#         - **User-Friendly**: Our intuitive interface ensures you can get started without a steep learning curve.  

#         Ready to find the perfect candidate? Use the sidebar to explore the features and start streamlining your recruitment process today!
#         """)
    
#     elif choice == "Profile Check":
#         st.title("Profile Check")
#         st.write("Upload your resume and enter a job description to see how well you fit the job.")

#         # Job description input with session state
#         if "job_description" not in st.session_state:
#             st.session_state.job_description = ""
#         job_description = st.text_area("Enter Job Description", height=150, value=st.session_state.job_description, placeholder="Atleast mention the Skills, Experience and JobRole")

#         # Resume upload with session state and reset mechanism
#         if "uploader_key" not in st.session_state:
#             st.session_state.uploader_key = 0
#         if "resume_file" not in st.session_state:
#             st.session_state.resume_file = None
#         if "resume_filename" not in st.session_state:
#             st.session_state.resume_filename = None
#         resume_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"], key=f"resume_uploader_{st.session_state.uploader_key}")
#         if resume_file:
#             st.session_state.resume_file = resume_file
#             st.session_state.resume_filename = resume_file.name

#         # Store analysis results in session state for one-time viewing
#         if "analysis_results" not in st.session_state:
#             st.session_state.analysis_results = {"job_desc": None, "resume": None, "comparison": None, "feedback": None}

#         # Add spacing before Analyze button
#         st.write(" ")  # Adds a single line of spacing

#         if st.button("Analyze"):
#             if not job_description:
#                 st.error("Please enter a job description.")
#             elif not resume_file:
#                 st.error("Please upload your resume.")
#             else:
#                 # Update session state with current inputs
#                 st.session_state.job_description = job_description
#                 st.session_state.resume_file = resume_file
#                 # Detect file type and extract text accordingly
#                 file_type = resume_file.type
#                 resume_text = ""
                
#                 if file_type == "application/pdf":
#                     st.write("Processing...")
#                     resume_text = pdf_to_text(resume_file)
#                 elif file_type == "text/plain":
#                     st.write("Processing...")
#                     resume_text = txt_to_text(resume_file)
#                 else:
#                     st.error("Unsupported file format. Please upload a PDF or TXT file.")
#                     return

#                 # Parse job description and resume
#                 job_desc_text = parse_job_description(job_description)
#                 resume_text = parse_resume_for_recruiter(resume_text)
#                 comparison_result = compare_job_and_resume(job_desc_text, resume_text) if job_desc_text and resume_text else None
#                 feedback_result = feedback_parse(job_desc_text, resume_text) if job_desc_text and resume_text else None

#                 # Store results in session state without saving to history
#                 st.session_state.analysis_results = {
#                     "job_desc": job_desc_text,
#                     "resume": resume_text,
#                     "comparison": comparison_result,
#                     "feedback": feedback_result
#                 }

#         # Add spacing between Analyze button and buttons row
#         st.write(" ")  # Adds a single line of spacing
#         st.write(" ")  # Adds a second line of spacing
#         st.write(" ")  # Adds a third line of spacing

#         # Display buttons only if analysis results are available
#         if st.session_state.analysis_results["job_desc"] is not None:
#             col1, col2, col3, col4 = st.columns(4)
#             with col1:
#                 if st.button("Job Description"):
#                     st.session_state.selected_section = "job_desc"
#             with col2:
#                 if st.button("Resume"):
#                     st.session_state.selected_section = "resume"
#             with col3:
#                 if st.button("Comparison"):
#                     st.session_state.selected_section = "comparison"
#             with col4:
#                 if st.button("Feedback"):
#                     st.session_state.selected_section = "feedback"

#             # Display selected content in full width
#             if "selected_section" in st.session_state:
#                 st.write("---")  # Separator for clarity
#                 if st.session_state.selected_section == "job_desc" and st.session_state.analysis_results["job_desc"]:
#                     st.text(st.session_state.analysis_results["job_desc"])
#                 elif st.session_state.selected_section == "resume" and st.session_state.analysis_results["resume"]:
#                     st.text(st.session_state.analysis_results["resume"])
#                 elif st.session_state.selected_section == "comparison" and st.session_state.analysis_results["comparison"]:
#                     st.write(st.session_state.analysis_results["comparison"])
#                 elif st.session_state.selected_section == "feedback" and st.session_state.analysis_results["feedback"]:
#                     st.write(st.session_state.analysis_results["feedback"])

#             # Add Clear and Save buttons below the output
#             col5, col6 = st.columns(2)
#             with col5:
#                 if st.button("Clear"):
#                     st.session_state.job_description = ""
#                     st.session_state.resume_file = None
#                     st.session_state.analysis_results = {"job_desc": None, "resume": None, "comparison": None, "feedback": None}
#                     st.session_state.uploader_key += 1  # Increment key to reset file uploader
#                     st.rerun()
#             with col6:
#                 if st.button("Save"):
#                     if st.session_state.resume_file:
#                         # Check if resume already exists
#                         resumes = get_user_resumes(st.session_state.user['id'])
#                         if resumes and any(resume[1] == st.session_state.resume_filename for resume in resumes):
#                             st.warning("It's already Liked.")
#                         else:
#                             try:
#                                 save_resume(st.session_state.user['id'], st.session_state.resume_file)
#                                 st.success(f"Resume '{st.session_state.resume_filename}' saved to Liked Resume.")
#                             except Exception as e:
#                                 st.error(f"Failed to save resume: {str(e)}")
#                     else:
#                         st.error("No resume uploaded to save.")

    
#     elif choice == "Liked Resume":
#         st.title("Liked Resume")
#         resumes = get_user_resumes(st.session_state.user['id'])
#         if resumes:
#             for resume in resumes:
#                 content = resume[3]  # file_content BLOB
#                 upload_date = resume[2]
#                 # Convert string to datetime object
#                 upload_date = datetime.strptime(upload_date, "%Y-%m-%d %H:%M:%S.%f")
#                 formatted_date = upload_date.strftime("%Y-%m-%d at %I:%M %p")
#                 st.subheader(resume[1])  # filename
#                 st.write(f"Saved on: {formatted_date}")
#                 # Provide download button for the file
#                 file_bytes = BytesIO(content)
#                 st.download_button(
#                     label="Download Resume",
#                     data=file_bytes,
#                     file_name=resume[1]
#                 )
#                 if resume[4]:  # analysis
#                     st.write("Analysis:", resume[4])

#             # Add Clear button to remove all resumes
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.button("Clear"):
#                     # Clear all resumes for the current user from the database
#                     clear_resumes(st.session_state.user['id'])
#                     st.success("All liked resumes have been cleared!")
#                     st.rerun()
#         else:
#             st.write("No resumes saved yet.")
    
    
#     elif choice == "More":
#         st.title("More Options")
#         st.write("Select an action below:")
        
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("Logout"):
#                 st.session_state.user = None
#                 st.session_state.page = 'login'
#                 st.success("Logged out successfully!")
#                 st.rerun()
#         with col2:
#             if st.button("Delete Account"):
#                 user_id = st.session_state.user['id']
#                 delete_account(user_id)
#                 st.session_state.user = None
#                 st.session_state.page = 'login'
#                 st.success("Account deleted successfully!")
#                 st.rerun()










#####################################################################################################################
# First one : Before Supabase Database

# import streamlit as st
# import PyPDF2
# from database import save_resume, get_user_resumes, download_resume, clear_resumes, delete_account
# from datetime import datetime
# from io import BytesIO
# from Gemini_services.services import parse_job_description, parse_resume_for_recruiter, compare_job_and_resume, feedback_parse

# # Helper function to extract text from a PDF
# def pdf_to_text(pdf_file):
#     reader = PyPDF2.PdfReader(pdf_file)
#     text = ""
#     for page_num in range(len(reader.pages)):
#         page = reader.pages[page_num]
#         text += page.extract_text()
#     return text

# # Helper function to extract text from a TXT file
# def txt_to_text(txt_file):
#     return txt_file.read().decode("utf-8")

# # Streamlit UI for Recruiter
# def recruiter_interface():
#     st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
#     menu = ["Homepage", "Profile Check", "Liked Resume", "More"]
#     choice = st.sidebar.selectbox("Menu", menu)
    
#     if choice == "Homepage":
#         st.title("Recruiter Homepage")
#         st.subheader(f"Welcome to SkillFit AI, {st.session_state.user['username']}!")
#         st.markdown("""
#         ### Unlock the Power of AI-Driven Recruitment

#         As a recruiter, you’re here to find the best talent for your organization, and **SkillFit AI** is designed to make that process smarter, faster, and more efficient. Powered by the Gemini API, our platform offers cutting-edge tools to help you evaluate candidates with precision and ease. Whether you're analyzing resumes, comparing them against job descriptions, or managing your favorite candidates, we’ve got you covered.

#         #### What You Can Do Here

#         **SkillFit AI** provides a tailored experience for recruiters through three key sections accessible from the sidebar:

#         1. **Profile Check**  
#            - **What It Does**: Upload a job description and a candidate’s resume to get a detailed analysis. Our AI extracts key details like job roles, experience, and skills from both documents, compares them, and provides a compatibility rating along with actionable feedback.  
#            - **Why It’s Useful**: Quickly identify if a candidate is a good fit for the role without manually sifting through documents. The AI-driven comparison ensures you focus on the most relevant candidates, saving you time and effort.  
#            - **How to Use It**: Navigate to “Profile Check,” upload a job description (TXT) and a resume (PDF or TXT), and click “Analyze” to see the results. You can also save promising resumes for later review.

#         2. **Liked Resume**  
#            - **What It Does**: View and manage all the resumes you’ve saved from the “Profile Check” section. Download resumes, review their details, or clear the list if needed.  
#            - **Why It’s Useful**: Keep track of top candidates in one place. This section acts as your personal shortlist, making it easy to revisit and compare your favorite profiles.  
#            - **How to Use It**: Go to “Liked Resume” to see your saved resumes. Use the “Download” button to retrieve a resume or the “Clear” button to remove all saved resumes.

#         3. **More Options**  
#            - **What It Does**: Access additional account management features, such as logging out or deleting your account.  
#            - **Why It’s Useful**: Securely manage your account with ease. If you’re done for the day, log out to keep your session safe. Need to remove your account? The “Delete Account” option ensures all your data (including saved resumes) is permanently deleted.  
#            - **How to Use It**: Navigate to “More,” then choose “Logout” to end your session or “Delete Account” to remove your profile.

#         #### Why Choose SkillFit AI?
#         - **AI-Powered Insights**: Leverage the Gemini API to parse and analyze documents with unparalleled accuracy.  
#         - **Time-Saving**: Automate the tedious parts of recruitment, so you can focus on what matters—building great teams.  
#         - **User-Friendly**: Our intuitive interface ensures you can get started without a steep learning curve.  

#         Ready to find the perfect candidate? Use the sidebar to explore the features and start streamlining your recruitment process today!
#         """)
    
#     elif choice == "Profile Check":
#         st.title("Profile Check")
#         st.write("Upload your resume and enter a job description to see how well you fit the job.")

#         # Job description input with session state
#         if "job_description" not in st.session_state:
#             st.session_state.job_description = ""
#         job_description = st.text_area("Enter Job Description", height=150, value=st.session_state.job_description, placeholder="Atleast mention the Skills, Experience and JobRole")

#         # Resume upload with session state and reset mechanism
#         if "uploader_key" not in st.session_state:
#             st.session_state.uploader_key = 0
#         if "resume_file" not in st.session_state:
#             st.session_state.resume_file = None
#         if "resume_filename" not in st.session_state:
#             st.session_state.resume_filename = None
#         resume_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"], key=f"resume_uploader_{st.session_state.uploader_key}")
#         if resume_file:
#             st.session_state.resume_file = resume_file
#             st.session_state.resume_filename = resume_file.name

#         # Store analysis results in session state for one-time viewing
#         if "analysis_results" not in st.session_state:
#             st.session_state.analysis_results = {"job_desc": None, "resume": None, "comparison": None, "feedback": None}

#         # Add spacing before Analyze button
#         st.write(" ")  # Adds a single line of spacing

#         if st.button("Analyze"):
#             if not job_description:
#                 st.error("Please enter a job description.")
#             elif not resume_file:
#                 st.error("Please upload your resume.")
#             else:
#                 # Update session state with current inputs
#                 st.session_state.job_description = job_description
#                 st.session_state.resume_file = resume_file
#                 # Detect file type and extract text accordingly
#                 file_type = resume_file.type
#                 resume_text = ""
                
#                 if file_type == "application/pdf":
#                     st.write("Processing...")
#                     resume_text = pdf_to_text(resume_file)
#                 elif file_type == "text/plain":
#                     st.write("Processing...")
#                     resume_text = txt_to_text(resume_file)
#                 else:
#                     st.error("Unsupported file format. Please upload a PDF or TXT file.")
#                     return

#                 # Parse job description and resume
#                 job_desc_text = parse_job_description(job_description)
#                 resume_text = parse_resume_for_recruiter(resume_text)
#                 comparison_result = compare_job_and_resume(job_desc_text, resume_text) if job_desc_text and resume_text else None
#                 feedback_result = feedback_parse(job_desc_text, resume_text) if job_desc_text and resume_text else None

#                 # Store results in session state without saving to history
#                 st.session_state.analysis_results = {
#                     "job_desc": job_desc_text,
#                     "resume": resume_text,
#                     "comparison": comparison_result,
#                     "feedback": feedback_result
#                 }

#         # Add spacing between Analyze button and buttons row
#         st.write(" ")  # Adds a single line of spacing
#         st.write(" ")  # Adds a second line of spacing
#         st.write(" ")  # Adds a third line of spacing

#         # Display buttons only if analysis results are available
#         if st.session_state.analysis_results["job_desc"] is not None:
#             col1, col2, col3, col4 = st.columns(4)
#             with col1:
#                 if st.button("Job Description"):
#                     st.session_state.selected_section = "job_desc"
#             with col2:
#                 if st.button("Resume"):
#                     st.session_state.selected_section = "resume"
#             with col3:
#                 if st.button("Comparison"):
#                     st.session_state.selected_section = "comparison"
#             with col4:
#                 if st.button("Feedback"):
#                     st.session_state.selected_section = "feedback"

#             # Display selected content in full width
#             if "selected_section" in st.session_state:
#                 st.write("---")  # Separator for clarity
#                 if st.session_state.selected_section == "job_desc" and st.session_state.analysis_results["job_desc"]:
#                     st.text(st.session_state.analysis_results["job_desc"])
#                 elif st.session_state.selected_section == "resume" and st.session_state.analysis_results["resume"]:
#                     st.text(st.session_state.analysis_results["resume"])
#                 elif st.session_state.selected_section == "comparison" and st.session_state.analysis_results["comparison"]:
#                     st.write(st.session_state.analysis_results["comparison"])
#                 elif st.session_state.selected_section == "feedback" and st.session_state.analysis_results["feedback"]:
#                     st.write(st.session_state.analysis_results["feedback"])

#             # Add Clear and Save buttons below the output
#             col5, col6 = st.columns(2)
#             with col5:
#                 if st.button("Clear"):
#                     st.session_state.job_description = ""
#                     st.session_state.resume_file = None
#                     st.session_state.analysis_results = {"job_desc": None, "resume": None, "comparison": None, "feedback": None}
#                     st.session_state.uploader_key += 1  # Increment key to reset file uploader
#                     st.rerun()
#             with col6:
#                 if st.button("Save"):
#                     if st.session_state.resume_file:
#                         # Check if resume already exists
#                         resumes = get_user_resumes(st.session_state.user['id'])
#                         if resumes and any(resume[1] == st.session_state.resume_filename for resume in resumes):
#                             st.warning("It's already Liked.")
#                         else:
#                             save_resume(st.session_state.user['id'], st.session_state.resume_file)
#                             st.success(f"Resume '{st.session_state.resume_filename}' saved to Liked Resume.")

#                     else:
#                         st.error("No resume uploaded to save.")

    
#     elif choice == "Liked Resume":
#         st.title("Liked Resume")
#         resumes = get_user_resumes(st.session_state.user['id'])
#         if resumes:
#             for resume in resumes:
#                 content = resume[3]  # file_content BLOB
#                 upload_date = resume[2]
#                 # Convert string to datetime object
#                 upload_date = datetime.strptime(upload_date, "%Y-%m-%d %H:%M:%S.%f")
#                 formatted_date = upload_date.strftime("%Y-%m-%d at %I:%M %p")
#                 st.subheader(resume[1])  # filename
#                 st.write(f"Saved on: {formatted_date}")
#                 # Provide download button for the file
#                 file_bytes = BytesIO(content)
#                 st.download_button(
#                     label="Download Resume",
#                     data=file_bytes,
#                     file_name=resume[1]
#                 )
#                 if resume[4]:  # analysis
#                     st.write("Analysis:", resume[4])

#             # Add Clear button to remove all resumes
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.button("Clear"):
#                     # Clear all resumes for the current user from the database
#                     clear_resumes(st.session_state.user['id'])
#                     st.success("All liked resumes have been cleared!")
#                     st.rerun()
#         else:
#             st.write("No resumes saved yet.")
    
    
#     elif choice == "More":
#         st.title("More Options")
#         st.write("Select an action below:")
        
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("Logout"):
#                 st.session_state.user = None
#                 st.session_state.page = 'login'
#                 st.success("Logged out successfully!")
#                 st.rerun()
#         with col2:
#             if st.button("Delete Account"):
#                 user_id = st.session_state.user['id']
#                 delete_account(user_id)
#                 st.session_state.user = None
#                 st.session_state.page = 'login'
#                 st.success("Account deleted successfully!")
#                 st.rerun()