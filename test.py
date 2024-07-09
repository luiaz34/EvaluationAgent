import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    # Extract text from all pages
    text = ""
    for page in doc:
        text += page.get_text()
    
    # Close the document
    doc.close()
    
    return text

def clean_text(text):
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters (you might want to adjust this)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def split_into_sections(text):
    # This is a basic split and might need adjustment based on CV format
    sections = re.split(r'\n(?=[A-Z]{2,})', text)
    return [section.strip() for section in sections if section.strip()]

# Path to your PDF CV
cv_path = r'C:\Users\khain\Documents\EvaluatingAgent\candidateCV.pdf'

# Extract text from PDF
cv_text = extract_text_from_pdf(cv_path)
print(cv_text)
# # Clean the extracted text
# cleaned_text = clean_text(cv_text)
# print(cleaned_text)

# # Split into sections
# cv_sections = split_into_sections(cleaned_text)
# # print(cv_sections)

# # Print sections (first 50 characters of each)
# for i, section in enumerate(cv_sections, 1):
#     print(f"Section {i}: {section[:50]}...")
#     print()