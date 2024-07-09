import os
from dotenv import load_dotenv
import anthropic
# from langchain_anthropic import ChatAnthropic
import fitz

# Load environment variables
load_dotenv()

# Define functions to read job description, interview transcript, and extract text from PDF
def readingJD():
    file_path = r"C:\Users\khain\Documents\EvaluatingAgent\JD.txt"
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        content = ""
    except IOError:
        print(f"An error occurred while reading the file at {file_path}.")
        content = ""
    return content

def readingtranscript():
    file_path = r"C:\Users\khain\Documents\EvaluatingAgent\goodTranscript.txt"
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        content = ""
    except IOError:
        print(f"An error occurred while reading the file at {file_path}.")
        content = ""
    return content

def readingPDF():
    pdf_path = r'C:\Users\khain\Documents\EvaluatingAgent\candidateCV.pdf'
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
    except FileNotFoundError:
        print(f"The file at {pdf_path} was not found.")
        text = ""
    except IOError:
        print(f"An error occurred while reading the file at {pdf_path}.")
        text = ""
    return text

# Read input data
job_description = readingJD()
interview_transcript = readingtranscript()
cv_text = readingPDF()

# Define the prompt template
template = """
You are a hiring agent or recruiter tasked with evaluating candidates for a specific job position. You will be provided with a job description, an interview transcript, and a candidate's CV. Your task is to evaluate the CV against the job description and interview transcript, provide a rating for the candidate, and suggest alternative roles if necessary.

First, carefully review the following job description:
<job_description>
{job_description}
</job_description>

Next, review the interview transcript:
<interview_transcript>
{interview_transcript}
</interview_transcript>

Now, examine the candidate's CV:
<cv>
{cv}
</cv>

To evaluate the candidate:

1. Compare the candidate's qualifications, skills, and experience in the CV with the requirements outlined in the job description.
2. Consider how well the candidate's responses in the interview transcript align with the job requirements and company culture.
3. Identify any strengths or weaknesses that stand out in the CV or interview transcript.

Based on your evaluation, rate the candidate on a scale of 1 to 10, where 1 is the lowest and 10 is the highest. Consider the following factors:
- Relevance of skills and experience to the job description
- Educational background
- Work history
- Achievements and accomplishments
- Interview performance

Before providing the final rating, explain your reasoning in detail. Include specific examples from the CV and interview transcript that support your evaluation.

If the candidate's rating is 5 or below, identify alternative roles that might be more suitable based on their skills, experience, and interests. Consider positions within the same company or industry that could be a better fit.

Format your response as follows:

<evaluation>
[Provide a detailed explanation of your evaluation, including specific examples from the CV and interview transcript]
</evaluation>

<rating>
[Candidate's Name]
[Rating (1-10)]
</rating>

<alternative_roles>
[If the rating is 5 or below, list 2-3 alternative roles that might be more suitable for the candidate, along with a brief explanation for each suggestion]
</alternative_roles>

Remember to be objective and fair in your assessment, focusing on the candidate's qualifications and potential fit for the position or alternative roles.
"""

# Initialize the ChatAnthropic client
key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=key)

# Create the message to be sent to the model
message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=4000,
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": template.format(job_description=job_description, interview_transcript=interview_transcript, cv=cv_text)
        }
    ]
)

# Print the response from the model
print(message.content[0].text)

