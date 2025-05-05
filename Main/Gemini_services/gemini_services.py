from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load the environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")



# Function to parse job description (from Recruiter.py)
def parse_job_description(job_description):
    response = model.generate_content(
        f"""
        You are an expert job description analyst.

        From the job description provided below, extract and return the following three fields as plain text:

        1. JobRole: Identify the main jobRole.
        2. Experience: Provide the required experience level.
        3. Skills: List the main skills required.

        **Important Instructions:**
        - Format the output as plain text with numbered sections as shown below:
          1. JobRole: (Mention the jobRole)
          2. Experience: (Mention the experience level)
          3. Skills: 
             - (Skill 1)
             - (Skill 2)
             - (Skill 3)
             - (Skill 4)
          - Add one blank line between each section.
          - No extra commentary.

        Job Description:
        {job_description}
        """
    )
    return response.text



# Function to parse resume text for Recruiter (from Recruiter.py)
def parse_resume_for_recruiter(resume_text):
    response = model.generate_content(
        f"""
            You are an expert resume analyst.

            From the candidate's resume text provided below, extract and return the following three fields as plain text:

            1. JobRole: Identify the main jobRole of the candidate, based on the candidate's work history.

            2. Experience:
            - First line: Write only the total professional experience in plain format.
                - If more than 1 year: Format as "X years Y months" (e.g., "8 years 2 months").
                - If less than 1 year: Format as "X months" (e.g., "10 months").
            - Add **one blank line** after the total experience line.

            - Then, provide a detailed paragraph summary of the candidate's professional experience, organized **company-wise**:
                - For each company:
                - On a new line, write the **Company Name**
                - Then write: **Role:** (Job Title)
                - Then write: **Duration:** (Start - End)
                - Then write a **detailed paragraph** describing the candidate's responsibilities, achievements, and contributions during their time at that company.
                - If the candidate worked at more than one company, insert **one blank line** between each company’s summary.
                - If the candidate worked at only one company, no need to add extra spacing.

            3. Skills:
            - Extract and list the candidate's main skills as bullet points.
            - Focus on both technical and soft skills mentioned in the resume.

            **Important Instructions:**
            - Format the output as plain text with numbered sections as shown below:
            1. JobRole: (Mention the jobRole)

            2. Experience:
                - (Total experience)

                (Company 1 summary)

                (Company 2 summary)

            3. Skills:
                - (Skill 1)
                - (Skill 2)
                - (Skill 3)
                - (Skill 4)

            - Add **one blank line** between each main section (JobRole, Experience, Skills).
            - Do not add any extra commentary or explanation.

            Resume Text:
            {resume_text}
        """
    )
    return response.text



# Function to parse resume for Candidate (from Candidate.py)
# def parse_resume_for_candidate(resume_text):
#     response = model.generate_content(
#         f"""
#         You are an expert resume analyst.

#         From the candidate's resume text provided below, extract and return the following three fields:

#         1. JobRole
#         2. Experience (special format instructions, with extra importance)
#         3. Skills

#         **Important Instructions:**
#         - **JobRole**: Identify the main jobRole candidate wants to apply for.
#         - **Experience**: Calculate the total professional experience by adding all durations from different companies.
#           - Format the experience naturally:
#             - **First bullet**: Write only the total experience in plain format (e.g., "2 years 4 months" or "10 months").
#               - If more than 1 year: "X years Y months" (e.g., "2 years 4 months").
#               - If less than 1 year: only months (e.g., "10 months").
#             - **Next Twenty bullets**: To give more importance to Experience, write Twenty short sentences about the experience, including the total experience in each sentence.
#               - Use different wording for each sentence.
        
#         - **Skills**: Extract and list the candidate's main skills normally.
#         - **Format the output as plain text** as shown below:

#           1. JobRole: (Mention the jobRole)

#           2. Experience:
#           - (Sentence 1 about experience)
#           - (Sentence 2 about experience)
#           - (Sentence 3 about experience)

#           3. Skills:
#           - (Skill 1)
#           - (Skill 2)
#           - (Skill 3)
#           - (Skill 4)
#           - (Skill 5)

#         - Add one blank line between each section.
#         - No extra commentary.

#         Resume Text:
#         {resume_text}
#         """
#     )
#     return response.text


def parse_resume_for_candidate(resume_text):
    response = model.generate_content(
        f"""
        You are an expert resume analyst.

        From the candidate's resume text provided below, extract and return the following three fields:

        1. JobRole
        2. Experience (special format instructions, with extra importance)
        3. Skills

        **Important Instructions:**
        - **JobRole**: Identify the main jobRole candidate wants to apply for.
        - **Experience**: Calculate the total professional experience by adding all durations from different companies.
          - Format the experience naturally:
            - **First bullet**: Write only the total experience in plain format (e.g., "2 years 4 months" or "10 months").
              - If more than 1 year: "X years Y months" (e.g., "2 years 4 months").
              - If less than 1 year: only months (e.g., "10 months").
        
        - **Skills**: Extract and list the candidate's main skills normally.
        - **Format the output as plain text** as shown below:

          1. JobRole: (Mention the jobRole)

          2. Experience: (Mention the experience)


          3. Skills:
          - (Skill 1)
          - (Skill 2)
          - (Skill 3)
          - (Skill 4)
          - (Skill 5)

        - Add one blank line between each section.
        - No extra commentary.

        Resume Text:
        {resume_text}
        """
    )
    return response.text






# Function to compare job description and resume (from Recruiter.py)
def compare_job_and_resume(job_text, resume_text):
    prompt = f"""
You are an AI assistant designed to evaluate how well a candidate's resume matches a job description.

Please strictly follow this output format, with no markdown, no extra formatting, and no headings. Your output must begin with the rating and the corresponding message from the provided scale.

---------------------
START OUTPUT FORMAT:
---------------------
Rating: <numeric>/10 : <corresponding message from the scale>  

JobRole Match: <score>/10 - <explanation>  
Experience Match: <score>/10 - <explanation>  
Skills Match: <score>/10 - <explanation>  

Why not a perfect 10?: <explanation if rating < 10, else write "N/A">
---------------------
END FORMAT
---------------------

Use this strict rating scale:

1/10: The resume doesn't meet any requirements of the job description.  
2/10: Very few aspects of the resume align with the job description.  
3/10: Some aspects of the resume are relevant, but there are significant gaps.  
4/10: The resume partially meets the job description with a few key areas lacking.  
5/10: The resume meets some of the key job requirements but has areas for improvement.  
6/10: The resume aligns with most aspects of the job description, with a few minor gaps.  
7/10: The resume matches the job description very well, with only minor areas for improvement.  
8/10: The resume almost perfectly matches the job description with one or two small gaps.  
9/10: The resume aligns with the job description almost perfectly, but there are very minor discrepancies.  
10/10: The resume fully matches the job description with no gaps or discrepancies.

Now begin the analysis.

Job Description:
{job_text}

Candidate Resume:
{resume_text}
"""
    response = model.generate_content(prompt)
    return response.text




# Function to parse feedback (from Recruiter.py)
def feedback_parse(job_text, resume_text):
    prompt = f"""
    Compare the following Job Description and Candidate Resume and provide a general assessment.
    Please do not include Markdown. Do not apply any visual styling to the text.

    Overall Assessment: Provide in not more than 3 words.

    Job Description Match: Based on the analysis of the resume, what type of job description would align best with the candidate’s current skill set? If applicable, suggest jobs that would be a better fit.

    Focus Areas for Improvement: If the user still wants to focus on the current job description (the one compared with), suggest a roadmap in paragraph.

    Job Description
    {job_text}

    Candidate Resume
    {resume_text}
    """
    response = model.generate_content(prompt)
    return response.text