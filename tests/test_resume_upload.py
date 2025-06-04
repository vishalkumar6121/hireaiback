import pytest
from pathlib import Path
import os

@pytest.fixture
def auth_token():
    """Create a test auth token"""
    return create_access_token(TEST_USER)

@pytest.fixture
def test_resume_file():
    """Get the path to the test resume file"""
    return Path("tests/data/Resume Vishal Kumar TL.pdf")

@pytest.fixture
def client():
    from main import app
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_upload_resume_success(client, auth_token, test_resume_file):
    """Test successful resume upload"""
    with open(test_resume_file, "rb") as f:
        response = client.post(
            f"/api/resumes/upload?token={auth_token}",
            files={"file": ("Resume Vishal Kumar TL.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "resume_url" in data
    assert data["message"] == "Resume uploaded successfully"

def test_upload_resume_with_candidate_id(auth_token, test_resume_file):
    """Test resume upload with specific candidate ID"""
    candidate_id = "test-candidate-id"
    with open(test_resume_file, "rb") as f:
        response = client.post(
            f"/api/resumes/upload?token={auth_token}",
            files={"file": ("Resume Vishal Kumar TL.pdf", f, "application/pdf")},
            data={"candidate_id": candidate_id}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "resume_url" in data

def test_upload_resume_invalid_token(test_resume_file):
    """Test resume upload with invalid token"""
    with open(test_resume_file, "rb") as f:
        response = client.post(
            "/api/resumes/upload?token=invalid_token",
            files={"file": ("Resume Vishal Kumar TL.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]

def test_upload_resume_no_token(test_resume_file):
    """Test resume upload without token"""
    with open(test_resume_file, "rb") as f:
        response = client.post(
            "/api/resumes/upload",
            files={"file": ("Resume Vishal Kumar TL.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 422
    assert "token" in response.json()["detail"][0]["loc"]

def test_upload_resume_invalid_file_type(auth_token):
    """Test resume upload with invalid file type"""
    # Create a test file with invalid extension
    test_file_path = Path("tests/test_resume.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")
    
    try:
        with open(test_file_path, "rb") as f:
            response = client.post(
                f"/api/resumes/upload?token={auth_token}",
                files={"file": ("test_resume.txt", f, "text/plain")}
            )
        
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
    finally:
        if test_file_path.exists():
            os.remove(test_file_path)

def test_upload_resume_empty_file(auth_token):
    """Test resume upload with empty file"""
    # Create an empty test file
    test_file_path = Path("tests/empty.pdf")
    with open(test_file_path, "wb") as f:
        f.write(b"")
    
    try:
        with open(test_file_path, "rb") as f:
            response = client.post(
                f"/api/resumes/upload?token={auth_token}",
                files={"file": ("empty.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 400
        assert "Empty file" in response.json()["detail"]
    finally:
        if test_file_path.exists():
            os.remove(test_file_path)

def test_upload_resume_large_file(auth_token):
    """Test resume upload with file exceeding size limit"""
    # Create a large test file (11MB)
    test_file_path = Path("tests/large.pdf")
    with open(test_file_path, "wb") as f:
        f.write(b"0" * (11 * 1024 * 1024))  # 11MB
    
    try:
        with open(test_file_path, "rb") as f:
            response = client.post(
                f"/api/resumes/upload?token={auth_token}",
                files={"file": ("large.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]
    finally:
        if test_file_path.exists():
            os.remove(test_file_path)

def test_upload_resume_missing_file(auth_token):
    """Test resume upload without file"""
    response = client.post(
        f"/api/resumes/upload?token={auth_token}"
    )
    
    assert response.status_code == 422
    assert "file" in response.json()["detail"][0]["loc"] 