import nltk
import os
import sys

# Download required NLTK data first
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('universal_tagset', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)

from fastapi import UploadFile, HTTPException, status
from dotenv import load_dotenv
import logging
from typing import Dict, List, Any
import tempfile
import spacy
import re
import pdfplumber
import io
from docx import Document
from supabase import create_client, Client
import uuid
import json
from pyresparser import ResumeParser

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model not found, download it
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content using pdfplumber."""
    try:
        pdf_file = io.BytesIO(file_content)
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                # Extract text with layout preservation
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                
                # Extract tables if any
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        text += " ".join([str(cell) for cell in row if cell]) + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from PDF file"
        )

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file content."""
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from DOCX file"
        )

def extract_text_from_file(file_content: bytes, content_type: str) -> str:
    """Extract text from file based on content type."""
    if content_type == "application/pdf":
        return extract_text_from_pdf(file_content)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_content)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {content_type}"
        )

def extract_skills(text: str) -> Dict[str, List[str]]:
    """Extract skills from text using enhanced pattern matching and context analysis."""
    doc = nlp(text.lower())
    
    # Define skill categories and their variations
    skill_categories = {
        "programming": {
            "python": ["python", "python programming", "python3", "python 3", "py", "django", "flask", "fastapi"],
            "java": ["java", "java programming", "j2ee", "spring", "hibernate", "maven"],
            "javascript": ["javascript", "js", "node.js", "nodejs", "react", "angular", "vue", "typescript", "ts"],
            "c++": ["c++", "cpp", "c plus plus", "stl", "boost"],
            "c#": ["c#", "csharp", "dotnet", ".net", "asp.net"],
            "ruby": ["ruby", "ruby on rails", "rails", "ror"],
            "php": ["php", "laravel", "symfony", "wordpress"],
            "swift": ["swift", "ios development", "xcode"],
            "kotlin": ["kotlin", "android development"],
            "go": ["go", "golang"],
            "rust": ["rust", "rust programming"],
            "css": ["css", "css3", "css3"],
            "html": ["html", "html5", "html5"],
        },
        "frameworks": {
            "react": ["react", "react.js", "reactjs", "redux", "next.js"],
            "angular": ["angular", "angularjs", "ng"],
            "vue": ["vue", "vue.js", "vuejs", "nuxt"],
            "django": ["django", "django framework"],
            "flask": ["flask", "flask framework"],
            "spring": ["spring", "spring boot", "spring framework"],
            "express": ["express", "express.js", "expressjs"],
            "node": ["node", "node.js", "nodejs", "express"],
            "laravel": ["laravel"],
            "silverstripe": ["silverstripe"],
            "rails": ["rails", "ruby on rails", "ror"]
        },
        "databases": {
            "mysql": ["mysql", "mariadb"],
            "postgresql": ["postgresql", "postgres", "pg"],
            "mongodb": ["mongodb", "mongo", "nosql"],
            "redis": ["redis", "redis cache"],
            "cassandra": ["cassandra", "apache cassandra"],
            "elasticsearch": ["elasticsearch", "elastic", "elk stack"],
            "dynamodb": ["dynamodb", "aws dynamodb"]
        },
        "cloud": {
            "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "cloudfront"],
            "azure": ["azure", "microsoft azure", "azure cloud"],
            "gcp": ["gcp", "google cloud", "google cloud platform"],
            "kubernetes": ["kubernetes", "k8s", "kubectl"],
            "docker": ["docker", "docker compose", "containerization"],
            "terraform": ["terraform", "iac", "infrastructure as code"]
        },
        "tools": {
            "git": ["git", "github", "gitlab", "bitbucket"],
            "jenkins": ["jenkins", "ci/cd", "continuous integration"],
            "jira": ["jira", "atlassian", "agile tools"],
            "confluence": ["confluence", "documentation"],
            "slack": ["slack", "team collaboration"],
            "agile": ["agile", "scrum", "kanban", "sprint"]
        },
        "ai_ml": {
            "machine_learning": ["machine learning", "ml", "supervised learning", "unsupervised learning"],
            "deep_learning": ["deep learning", "neural networks", "cnn", "rnn", "lstm"],
            "tensorflow": ["tensorflow", "tf", "keras"],
            "pytorch": ["pytorch", "torch"],
            "scikit": ["scikit-learn", "sklearn", "scikit"],
            "nlp": ["nlp", "natural language processing", "text mining"],
            "computer_vision": ["computer vision", "cv", "image processing", "opencv"]
        },
        "payment_gateways": {
            "stripe": ["stripe", "stripe payment"],
            "paypal": ["paypal", "paypal payment"],
            "razorpay": ["razorpay", "razorpay payment"],
            "authorizenet": ["authorizenet", "authorizenet payment", "authorize.net", "authorize.net payment"],
        }
    }
    
    found_skills = {category: [] for category in skill_categories}
    text_lower = text.lower()
    
    # Extract skills using enhanced pattern matching
    for category, skills in skill_categories.items():
        for skill, variations in skills.items():
            # Check for any variation of the skill
            if any(var in text_lower for var in variations):
                # Get context around the skill mention
                for var in variations:
                    if var in text_lower:
                        # Find all occurrences of the skill
                        for match in re.finditer(r'\b' + re.escape(var) + r'\b', text_lower):
                            # Get surrounding context (50 characters before and after)
                            start = max(0, match.start() - 50)
                            end = min(len(text_lower), match.end() + 50)
                            context = text_lower[start:end]
                            
                            # Check if the skill is mentioned in a positive context or in a skill list
                            positive_indicators = [
                                "proficient", "experienced", "expert", "skilled",
                                "knowledge", "familiar", "worked with", "using",
                                "developed", "implemented", "created", "built",
                                "skills", "technologies", "stack", "tools",
                                "particulars", "expertise", "proficient in",
                                "experienced with", "familiar with"
                            ]
                            
                            # Check if the skill is in a list (comma-separated or in a skills section)
                            is_in_list = (
                                "," in context or
                                "skills" in context.lower() or
                                "technologies" in context.lower() or
                                "stack" in context.lower() or
                                "particulars" in context.lower()
                            )
                            
                            if any(indicator in context.lower() for indicator in positive_indicators) or is_in_list:
                                if skill not in found_skills[category]:
                                    found_skills[category].append(skill)
                                break
    
    return found_skills

def extract_education(text: str) -> List[Dict[str, str]]:
    """Extract education information using spaCy."""
    doc = nlp(text)
    education = []
    
    # Look for education-related patterns
    education_patterns = [
        r"(?i)(bachelor|master|phd|b\.?s\.?|m\.?s\.?|b\.?e\.?|m\.?e\.?)",
        r"(?i)(university|college|institute|school)",
        r"(?i)(computer science|engineering|information technology|it)"
    ]
    
    for pattern in education_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            # Get surrounding context
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            education.append({"context": context})
    
    return education

def extract_experience(text: str) -> List[Dict[str, str]]:
    """Extract work experience using spaCy."""
    doc = nlp(text)
    experience = []
    
    # Look for experience-related patterns
    experience_patterns = [
        r"(?i)(years? of experience)",
        r"(?i)(senior|junior|lead|principal)",
        r"(?i)(developer|engineer|architect|consultant)"
    ]
    
    for pattern in experience_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            # Get surrounding context
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            experience.append({"context": context})
    
    return experience

def extract_personal_info(text: str) -> Dict[str, str]:
    """Extract personal information using spaCy."""
    doc = nlp(text)
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else ""
    
    # Extract phone number
    phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group(0) if phone_match else ""
    
    # Extract name (first sentence usually contains the name)
    name = text.split('\n')[0].strip() if text else ""
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": "",  # Location extraction would require more complex NLP
        "summary": ""    # Summary extraction would require more complex NLP
    }

async def parse_resume_pyresparser(file: UploadFile) -> Dict[str, Any]:
    """Parse resume using pyresparser library."""
    try:
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file received"
            )
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Parse resume using pyresparser
            data = ResumeParser(temp_file_path).get_extracted_data()
            
            # Structure the extracted information
            extracted_info = {
                "skills": {
                    "technical": data.get("skills", []),
                    "soft_skills": []  # pyresparser doesn't distinguish between technical and soft skills
                },
                "education": [
                    {
                        "degree": edu.get("degree", ""),
                        "institution": edu.get("institution", ""),
                        "year": edu.get("year", "")
                    }
                    for edu in data.get("education", [])
                ],
                "experience": [
                    {
                        "company": exp.get("company", ""),
                        "position": exp.get("position", ""),
                        "duration": exp.get("duration", ""),
                        "description": exp.get("description", "")
                    }
                    for exp in data.get("experience", [])
                ],
                "personal_info": {
                    "name": data.get("name", ""),
                    "email": data.get("email", ""),
                    "phone": data.get("phone", ""),
                    "location": data.get("location", ""),
                    "summary": data.get("summary", "")
                },
                "filename": file.filename,
                "content_type": file.content_type
            }
            
            logger.debug(f"Parsed resume data using pyresparser: {json.dumps(extracted_info, indent=2)}")
            
            return extracted_info
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Resume parsing failed with pyresparser: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume: {str(e)}"
        )

async def parse_resume(file: UploadFile, parser_type: str = "spacy") -> Dict[str, Any]:
    """Parse resume using the specified parser type."""
    if parser_type == "pyresparser":
        return await parse_resume_pyresparser(file)
    else:
        # Use the existing spaCy-based implementation
        try:
            # Read file content
            file_content = await file.read()
            
            if not file_content:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Empty file received"
                )
            
            # Extract text from file
            text = extract_text_from_file(file_content, file.content_type)
            
            # Extract information using spaCy
            skills = extract_skills(text)
            education = extract_education(text)
            experience = extract_experience(text)
            personal_info = extract_personal_info(text)
            
            extracted_info = {
                "skills": skills,
                "education": education,
                "experience": experience,
                "personal_info": personal_info,
                "filename": file.filename,
                "content_type": file.content_type
            }
            
            # logger.debug(f"Parsed resume data using spaCy: {extracted_info}")
            
            return extracted_info
            
        except Exception as e:
            logger.error(f"Resume parsing failed with spaCy: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse resume: {str(e)}"
            )

async def upload_resume(file: UploadFile, user_id: str) -> dict:
    """Upload resume to Supabase storage and update user record."""
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    try:
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file received"
            )
        
        logger.debug(f"Uploading file {file.filename} to Supabase storage")
        
        # Upload to Supabase Storage
        result = supabase.storage.from_("resumes").upload(
            unique_filename,
            file_content,
            {"content-type": file.content_type}
        )
        
        logger.debug(f"Storage upload result: {result}")
        
        # Get public URL
        url = supabase.storage.from_("resumes").get_public_url(unique_filename)
        logger.debug(f"Generated public URL: {url}")
        
        try:
            # Update user's resume URL in the database
            update_data = {
                "resume_url": url,
                "resume_filename": file.filename
            }
            
            logger.debug(f"Updating user record with data: {update_data}")
            
            # Update user record
            db_result = supabase.table("users")\
                .update(update_data)\
                .eq("id", user_id)\
                .execute()
                
            logger.debug(f"Database update result: {db_result}")
            
        except Exception as db_error:
            logger.error(f"Database update failed: {str(db_error)}")
            # Don't raise the error, just log it and continue
            # The file is still uploaded successfully
        
        return {
            "resume_url": url,
            "filename": file.filename,
            "message": "Resume uploaded successfully"
        }
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        # If upload failed, try to clean up
        try:
            logger.debug(f"Attempting to clean up file: {unique_filename}")
            supabase.storage.from_("resumes").remove([unique_filename])
        except Exception as cleanup_error:
            logger.error(f"Cleanup failed: {str(cleanup_error)}")
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume: {str(e)}"
        ) 