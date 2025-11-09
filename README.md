# SkillFit AI

[**Live Demo**](https://skillfit-ai.streamlit.app/)

SkillFit AI is a Streamlit-based web application designed to streamline the recruitment process by leveraging AI to match skills to job requirements. It offers two primary interfaces: one for recruiters to analyze candidate resumes against job descriptions, and another for candidates to find job recommendations based on their resumes. Powered by the Gemini API, SkillFit AI provides intelligent parsing, comparison, and feedback to ensure the best skill-to-job fit.
<br>

## Table of Contents
- [Features](#features)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)

<br>

## Features

### Recruiter Interface
- **Job Description Parsing**: Extracts key details (Job Role, Experience, Skills) from job descriptions.
- **Resume Parsing**: Analyzes candidate resumes to extract Job Role, detailed Experience, and Skills.
- **Comparison & Feedback**: Compares resumes to job descriptions with a detailed rating (e.g., Job Role Match, Experience Match, Skills Match) and provides actionable feedback.
- **Save Resumes**: Allows recruiters to save promising resumes for later review in the "Liked Resume" section.

### Candidate Interface
- **Resume Parsing**: Extracts Job Role, Experience (with weighted importance), and Skills from candidate resumes.
- **Job Recommendations**: Matches resumes to a dataset of job descriptions (`job_descriptions.csv`) using TF-IDF and cosine similarity, recommending the top 5 jobs with clickable application links.

### General Features
- **User Authentication**: Supports user signup and login for recruiters and candidates.
- **Account Management**: Users can log out or delete their accounts, including all associated data (e.g., saved resumes).
- **AI-Powered**: Utilizes the Gemini API for intelligent text parsing and analysis.

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

## Technologies Used

- **Frontend**: Streamlit
- **Backend**: Python
- **Resume Analysis**: Gemini API for extracting skills, experience, and job roles
- **Job Matching**: NLP techniques using `TfidfVectorizer` and `cosine_similarity` from `scikit-learn`
- **Web Scraping**: Libraries like `beautifulsoup4` and `requests` for scraping job listings from Naukri.com
- **Email Service**: SMTP (Gmail) for sending verification codes
- **Database**: Supabase
- **Environment Variables**: Streamlit env

<br>

## Project Structure

SkillFit-AI/<br>
├── Main/<br>
│   ├── Gemini_services/<br>
│   │   └── gemini_services.py<br>
│   │<br>
│   ├── interfaces/  <br>
│   │   ├── Recruiter.py<br>
│   │   └── Candidate.py<br>
│   │<br>
│   ├── Web_Scrapping/  <br>
│   │   ├── job_descriptions.csv<br>
│   │   └── WebScrapping.ipynb<br>
│   │<br>
│   ├── .env  <br>
│   ├── .gitignore <br>
│   ├── app.py  <br>
│   ├── auth.py <br>
│   ├── database.py<br>
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


2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
* Create a .env file in the root directory.
* Add your Gemini API key:
GEMINI_API_KEY=your-api-key-here

   Create a `.env` file in the project root and add the following:
   ```plaintext
   GMAIL_USER=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   GEMINI_API_KEY=your-gemini-api-key

   [supabase]
   url = "https://your-supabase-url.supabase.co"
   key = "your-supabase-key.here
   ```
   Replace `your-email@gmail.com` with your Gmail address, `your-app-password` with a Gmail App Password (generate one in your Google Account settings), and `your-gemini-api-key` with your Gemini API key.

<br>

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   The app will be available at `http://localhost:8501`.

<br>


