# SkillFit AI – Ensures the Best Skill-to-Job Fit

SkillFit AI is a Streamlit-based web application designed to streamline the recruitment process by leveraging AI to match skills to job requirements. It offers two primary interfaces: one for recruiters to analyze candidate resumes against job descriptions, and another for candidates to find job recommendations based on their resumes. Powered by the Gemini API, SkillFit AI provides intelligent parsing, comparison, and feedback to ensure the best skill-to-job fit.
<br>

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)

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

## Project Structure

SkillFit-AI/<br><br>
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
│   │<br>
├── README.md <br>


<br>

## Technologies Used
- **Python 3.8+**: Core programming language.
- **Streamlit**: For building the web interface.
- **Gemini API**: For AI-powered parsing and analysis.
- **Pandas & Scikit-Learn**: For job recommendation logic (TF-IDF, cosine similarity).
- **PyPDF2**: For extracting text from PDF resumes.
- **python-dotenv**: For managing environment variables.

<br>

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Git
- A Gemini API key (obtain from [Google AI](https://ai.google.dev/))

<br>

### Steps
1. **Clone the Repository**:
   ```
   bash
   git clone https://github.com/Umer2900/SkillFit-AI.git
   cd SkillFit-AI


2. **Set Up a Virtual Environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt

4. **Configure Environment Variables**:
* Create a .env file in the root directory.
* Add your Gemini API key:
GEMINI_API_KEY=your-api-key-here

<br>

5. **Run the Application**:
   ```
   streamlit run app.py


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
