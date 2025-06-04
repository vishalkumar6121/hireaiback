import pytest
from fastapi import status

def test_get_templates(client, auth_headers, test_template):
    # Create a template first
    client.post(
        "/api/outreach/templates",
        headers=auth_headers,
        json=test_template
    )
    
    # Get all templates
    response = client.get("/api/outreach/templates", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_template["name"]

def test_create_template(client, auth_headers, test_template):
    response = client.post(
        "/api/outreach/templates",
        headers=auth_headers,
        json=test_template
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == test_template["name"]
    assert data["subject"] == test_template["subject"]
    assert data["body"] == test_template["body"]
    assert "id" in data

def test_send_outreach(client, auth_headers, test_candidate, test_template):
    # Create a candidate first
    candidate_response = client.post(
        "/api/candidates/",
        headers=auth_headers,
        json=test_candidate
    )
    candidate_id = candidate_response.json()["id"]
    
    # Create a template
    template_response = client.post(
        "/api/outreach/templates",
        headers=auth_headers,
        json=test_template
    )
    template_id = template_response.json()["id"]
    
    # Send outreach message
    outreach_data = {
        "candidate_id": candidate_id,
        "template_id": template_id,
        "status": "pending"
    }
    
    response = client.post(
        "/api/outreach/send",
        headers=auth_headers,
        json=outreach_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["candidate_id"] == candidate_id
    assert data["template_id"] == template_id
    assert data["status"] == "pending"
    assert "id" in data

def test_send_outreach_invalid_candidate(client, auth_headers, test_template):
    # Create a template
    template_response = client.post(
        "/api/outreach/templates",
        headers=auth_headers,
        json=test_template
    )
    template_id = template_response.json()["id"]
    
    # Try to send outreach with invalid candidate
    outreach_data = {
        "candidate_id": "invalid-id",
        "template_id": template_id,
        "status": "pending"
    }
    
    response = client.post(
        "/api/outreach/send",
        headers=auth_headers,
        json=outreach_data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_send_outreach_invalid_template(client, auth_headers, test_candidate):
    # Create a candidate
    candidate_response = client.post(
        "/api/candidates/",
        headers=auth_headers,
        json=test_candidate
    )
    candidate_id = candidate_response.json()["id"]
    
    # Try to send outreach with invalid template
    outreach_data = {
        "candidate_id": candidate_id,
        "template_id": "invalid-id",
        "status": "pending"
    }
    
    response = client.post(
        "/api/outreach/send",
        headers=auth_headers,
        json=outreach_data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND 