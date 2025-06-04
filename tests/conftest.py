import os
import sys
import pytest
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from main import app
from fastapi.testclient import TestClient
from app.services.auth import create_access_token

load_dotenv()

# Create test client
client = TestClient(app)

# Test data
TEST_USER = {
    "email": "vishal.kumar.6121+7@gmail.com",
    "full_name": "Test User",
    "role": "recruiter"
}

@pytest.fixture
def test_user():
    """Test user data for registration and login"""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "recruiter",
        "password": "testpassword123",
        "confirmPassword": "testpassword123"
    }

@pytest.fixture
def test_candidate():
    """Test candidate data"""
    return {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "location": "New York",
        "skills": ["python", "fastapi"],
        "experience_years": 5,
        "current_role": "Senior Developer",
        "desired_role": "Tech Lead"
    }

@pytest.fixture
def test_template():
    """Test outreach template data"""
    return {
        "name": "Initial Outreach",
        "subject": "Interested in your profile",
        "body": "Hello {candidate_name}, I came across your profile...",
        "category": "initial"
    }

@pytest.fixture
def auth_token():
    """Create a test auth token"""
    return create_access_token(TEST_USER)

@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers with token"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def test_resume_file():
    """Get the path to the test resume file"""
    return Path("tests/data/Resume Vishal Kumar TL.pdf")

@pytest.fixture
def test_resume_content():
    """Get the content of the test resume file"""
    resume_path = Path("tests/data/Resume Vishal Kumar TL.pdf")
    with open(resume_path, "rb") as f:
        return f.read()

@pytest.fixture
def test_resume_filename():
    """Get the filename of the test resume"""
    return "Resume Vishal Kumar TL.pdf"

@pytest.fixture
def test_resume_mimetype():
    """Get the MIME type of the test resume"""
    return "application/pdf"

@pytest.fixture
def client():
    from main import app
    from fastapi.testclient import TestClient
    return TestClient(app) 