import pytest
from fastapi import status

def test_get_analytics(client, auth_headers, test_candidate, test_template):
    # Create a candidate
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
    
    # Send an outreach message
    outreach_data = {
        "candidate_id": candidate_id,
        "template_id": template_id,
        "status": "pending"
    }
    client.post(
        "/api/outreach/send",
        headers=auth_headers,
        json=outreach_data
    )
    
    # Get analytics
    response = client.get("/api/analytics", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify analytics data structure
    assert "total_candidates" in data
    assert "status_distribution" in data
    assert "outreach_stats" in data
    assert "top_skills" in data
    
    # Verify specific values
    assert data["total_candidates"] > 0
    assert isinstance(data["status_distribution"], dict)
    assert isinstance(data["outreach_stats"], dict)
    assert isinstance(data["top_skills"], list)
    
    # Verify outreach stats
    assert "total_outreach" in data["outreach_stats"]
    assert "successful_outreach" in data["outreach_stats"]
    assert data["outreach_stats"]["total_outreach"] > 0

def test_get_analytics_no_data(client, auth_headers):
    # Get analytics with no data
    response = client.get("/api/analytics", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify analytics data structure with no data
    assert data["total_candidates"] == 0
    assert data["status_distribution"] == {}
    assert data["outreach_stats"]["total_outreach"] == 0
    assert data["outreach_stats"]["successful_outreach"] == 0
    assert data["top_skills"] == [] 