import pytest
from fastapi import status

def test_create_candidate(client, auth_headers, test_candidate):
    response = client.post(
        "/api/candidates/",
        headers=auth_headers,
        json=test_candidate
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == test_candidate["name"]
    assert data["email"] == test_candidate["email"]
    assert data["phone"] == test_candidate["phone"]
    assert "id" in data

def test_get_candidates(client, auth_headers, test_candidate):
    # Create a candidate first
    client.post(
        "/api/candidates/",
        headers=auth_headers,
        json=test_candidate
    )
    
    # Get all candidates
    response = client.get("/api/candidates/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_candidate["name"]

def test_get_candidate(client, auth_headers, test_candidate):
    # Create a candidate first
    create_response = client.post(
        "/api/candidates/",
        headers=auth_headers,
        json=test_candidate
    )
    candidate_id = create_response.json()["id"]
    
    # Get the specific candidate
    response = client.get(f"/api/candidates/{candidate_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == candidate_id
    assert data["name"] == test_candidate["name"]

def test_update_candidate(client, auth_headers, test_candidate):
    # Create a candidate first
    create_response = client.post(
        "/api/candidates/",
        headers=auth_headers,
        json=test_candidate
    )
    candidate_id = create_response.json()["id"]
    
    # Update the candidate
    update_data = {
        "name": "Updated Name",
        "email": "updated@example.com",
        "phone": "9876543210",
        "location": "New York",
        "skills": ["Python", "FastAPI", "Testing"],
        "experience": 5,
        "roles": ["Senior Developer"]
    }
    
    response = client.put(
        f"/api/candidates/{candidate_id}",
        headers=auth_headers,
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]

def test_delete_candidate(client, auth_headers, test_candidate):
    # Create a candidate first
    create_response = client.post(
        "/api/candidates/",
        headers=auth_headers,
        json=test_candidate
    )
    candidate_id = create_response.json()["id"]
    
    # Delete the candidate
    response = client.delete(f"/api/candidates/{candidate_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Verify the candidate is deleted
    get_response = client.get(f"/api/candidates/{candidate_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND 