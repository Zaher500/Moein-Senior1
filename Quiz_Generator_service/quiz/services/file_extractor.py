import os
import PyPDF2
from docx import Document

def extract_text_from_file(file_obj, filename):
    text = ""
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext == '.pdf':
            reader = PyPDF2.PdfReader(file_obj)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif ext in ['.docx', '.doc']:
            doc = Document(file_obj)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
    except Exception as e:
        raise ValueError(f"Failed to extract text from {filename}: {str(e)}")
        
    return text.strip()
