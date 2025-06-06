from typing import Dict, Any, Optional
import spacy
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import PyPDF2
from docx import Document
import io
import os
from dotenv import load_dotenv

load_dotenv()

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize LangChain with Groq
llm = ChatGroq(
    model="llama3-70b-8192",  # or another Groq-supported model
    api_key=os.getenv("GROQ_API_KEY")
)

class ResumeData(BaseModel):
    """Schema for parsed resume data"""
    full_name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    phone: Optional[str] = Field(description="Phone number")
    skills: list[str] = Field(description="List of technical and soft skills")
    experience: list[Dict[str, Any]] = Field(description="List of work experiences with company, role, duration, and description")
    education: Optional[list[Dict[str, Any]]] = Field(default=None, description="List of educational qualifications")
    summary: Optional[str] = Field(default=None, description="Professional summary or objective")
    years_of_experience: Optional[float] = Field(default=None, description="Total years of experience")

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    pdf_file = io.BytesIO(file_content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    docx_file = io.BytesIO(file_content)
    doc = Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_file(file_content: bytes, file_extension: str) -> str:
    """Extract text from different file formats"""
    if file_extension.lower() == '.pdf':
        return extract_text_from_pdf(file_content)
    elif file_extension.lower() == '.docx':
        return extract_text_from_docx(file_content)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def extract_skills(text: str) -> list[str]:
    """Extract skills using spaCy NLP"""
    doc = nlp(text)
    
    # Common technical skills to look for
    technical_skills = {
        "python", "java", "javascript", "typescript", "react", "angular", "vue",
        "node.js", "express", "django", "flask", "fastapi", "sql", "nosql",
        "mongodb", "postgresql", "mysql", "aws", "azure", "gcp", "docker",
        "kubernetes", "ci/cd", "git", "agile", "scrum", "machine learning",
        "ai", "data science", "big data", "spark", "hadoop"
    }
    
    # Extract skills using NLP
    skills = set()
    for token in doc:
        if token.text.lower() in technical_skills:
            skills.add(token.text.lower())
    
    return list(skills)

async def parse_resume(file_content: bytes, file_extension: str) -> Dict[str, Any]:
    """Parse resume using LLM and NLP"""
    # Extract text from file
    text = extract_text_from_file(file_content, file_extension)
    
    # Extract skills using NLP
    skills = extract_skills(text)
    
    # Create prompt for LLM
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert resume parser. Your task is to extract key information from a resume and output it as a JSON object strictly following the provided schema. Do not include any extra text, explanations, or markdown formatting (like ```json) outside of the JSON object itself. Only output the raw JSON.
        
        Extract the following information:
        - Full name
        - Email address
        - Phone number
        - Work experience (list of entries with company, role, duration, and description. Each entry must be a single JSON object with no duplicate keys.)
        - Education (list of entries with institution, degree, and year)
        - Professional summary
        - Total years of experience (as a number)

        Format the output as a JSON object matching the ResumeData schema. Ensure all keys match the schema exactly."""),
        ("user", "Here is the resume text:\n{text}\n\n{format_instructions}")
    ])
    
    # Create output parser
    parser = PydanticOutputParser(pydantic_object=ResumeData)
    
    # Create a chain to get raw LLM output
    raw_output_chain = prompt | llm
    
    # Get format instructions from the parser
    format_instructions = parser.get_format_instructions()

    # Parse resume
    try:
        # Get raw output from the LLM
        raw_llm_output = await raw_output_chain.ainvoke({"text": text, "format_instructions": format_instructions})
        print("Raw LLM Output:", raw_llm_output)

        # Parse the raw output using Pydantic parser
        result = parser.invoke(raw_llm_output)
        
        # Add extracted skills to the result
        result_dict = result.dict()
        result_dict["skills"] = skills
        
        return result_dict
    except Exception as e:
        print("Error during parsing:", str(e))
        # Re-raise a more informative error
        raise Exception(f"Failed to parse resume: {str(e)}") 