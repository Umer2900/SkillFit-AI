# SkillFit AI
**AI-Powered Resume Screening & Job Matching Platform**

<!-- [**Live Demo**](https://skillfit-ai.streamlit.app/) -->

SkillFit AI is a Streamlit-based web application designed to streamline the recruitment process by leveraging AI to match skills to job requirements. It offers two primary interfaces: one for recruiters to analyze candidate resumes against job descriptions, and another for candidates to find job recommendations based on their resumes. Powered by the Gemini API, SkillFit AI provides intelligent parsing, comparison, and feedback to ensure the best skill-to-job fit.
<br>

---

## 🎥 Candidate Side Demo

![Candidate Side Demo](Main/assets/Demo1.gif)

---


## Table of Contents
- [Why SkillFit AI Exists](#exists)
- [Features](#features)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)

<br>

---

## Why SkillFit AI Exists

Recruiters waste **10+ hours** per role reading bad resumes.  
Candidates apply to **100 jobs** → get **0 replies**.  

**We fixed both.**

- **For Recruiters**: Upload a ZIP of resumes + job description → Get **only the best matches** (≥7/10)  
- **For Candidates**: Upload your resume → Get **5 perfect jobs** with direct apply links  

**No resume is ever saved. Privacy by design.**


---

## Features

### Recruiter Side (The Power Tool)

**Bulk Resume Screening** *(Star Feature)*  
- Upload **ZIP with 500+ resumes** (PDF/TXT)  
- Paste job description  
- AI scores every resume vs JD  
- **Download only Passed (≥7/10)** as:  
  → `filtered_top_resumes.zip`  
  → `screening_results.csv` (Rating shown as `10/10` — no date bugs!)  
- Live progress bar + processing status  
- **Clear button** → Everything gone in 1 click  

**Profile Check**  
- Upload 1 resume + JD → Get instant 10/10 score  
- View parsed JD, resume, comparison, feedback  
- No "Save" button — **zero clutter**

### Candidate Side (Your Career GPS)

**Job Recommendation System**  
- Upload resume → AI extracts skills, experience, role  
- Matches against **10,000+ real jobs** (scraped from Naukri)  
- Returns **Top 5 perfect matches** with:  
  → Company | Role | Skills Match | **Apply Link** (clickable)  
- From blind applications → **sniper precision**

### General Features
- **User Authentication**: Supports user signup and login for recruiters and candidates.
- **Account Management**: Users can log out or delete their accounts.
---

<br>

## Usage

### 1. Sign Up or Log In:
- Choose your user type (Recruiter or Candidate) and create an account or log in.

### 2. Recruiter Interface:
- Navigate to "Profile Check" to upload a job description and a candidate resume (PDF or TXT).
- Click "Analyze" to parse and compare the job description and resume.
- View detailed results (Job Description, Resume, Comparison, Feedback).
- Save promising resumes to "Liked Resume" for later review.
- Use the "More" menu to log out or delete your account.

### 3. Candidate Interface:
- Navigate to "Job Recommendation" and upload your resume (PDF).
- Click "Find Jobs" to get the top 5 job recommendations based on your resume.
- Use the "More" menu to log out or delete your account.

<br>

---

## Tech Stack (100% Python)

| Layer           | Technology                     |
|-----------------|--------------------------------|
| Frontend        | Streamlit                      |
| AI Brain        | Google Gemini Pro API          |
| Backend         | Python (PyPDF2, zipfile, pandas, csv) |
| Web Scraping    | Libraries like `beautifulsoup4` and `requests` for scraping job listings from Naukri.com |
| Database        | Supabase (auth only)           |
| Auth            | Email + SHA-256                |
| Deployment      | Streamlit Cloud                |
| File Processing | In-memory (BytesIO) — **no storage** |

**Zero JavaScript. Zero bloat. Pure speed.**

---

<br>

## Project Structure

SkillFit-AI/<br>
├── Main/<br>
│   ├── Gemini_services/<br>
│   │   └── gemini_services.py<br>
│   │<br>
│   ├── interfaces/  <br>
│   │   ├── Recruiter.py    ← Bulk + Profile Check<br>
│   │   └── Candidate.py    ← Job Recommendations<br>
│   │<br>
│   ├── Web_Scrapping/  <br>
│   │   ├── job_descriptions.csv<br>
│   │   └── WebScrapping.ipynb<br>
│   │<br>
│   ├── .streamlit/  <br>
│   │   └── secrets.toml <br>
│   │<br>
│   ├── .gitignore <br>
│   ├── app.py  <br>
│   ├── auth.py <br>
│   ├── database.py   ← Only auth + delete<br>
│   ├── requirements.txt <br>
│<br>
├── README.md <br>


<br>


## Setup Instructions

### Prerequisites

To run SkillFit AI locally, ensure you have the following installed:
- Python 3.8+
- Git
- Streamlit
- Required Python packages (listed in `requirements.txt`)
- A Gmail account with an App Password for email verification
- Access to the Gemini API (configure API key as needed)

<br>

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Umer2900/SkillFit-AI.git
   cd SkillFit-AI
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Streamlit Secret Variables**:

   Create a `secrets.toml` file in the project root and add the following:
   ```plaintext
   GMAIL_USER=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   GEMINI_API_KEY=your-gemini-api-key

   [supabase]
   url = "https://your-supabase-url.supabase.co"
   key = "your-supabase-anon-key"
   ```
   Replace `your-email@gmail.com` with your Gmail address, `your-app-password` with a Gmail App Password (generate one in your Google Account settings), and `your-gemini-api-key` with your Gemini API key.

<br>

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   The app will be available at `http://localhost:8501`.

<br>