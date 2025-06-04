import pytest
from fastapi import status

def test_register_user(client, test_user):
    response = client.post("/api/auth/signup", json=test_user)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["full_name"] == test_user["full_name"]
    assert data["role"] == test_user["role"]
    assert "id" in data

def test_register_duplicate_user(client, test_user):
    # First registration
    client.post("/api/auth/signup", json=test_user)
    
    # Try to register the same user again
    response = client.post("/api/auth/signup", json=test_user)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success(client, test_user):
    # Register user first
    client.post("/api/auth/signup", json=test_user)
    
    # Try to login
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_logout(client, auth_headers):
    response = client.post("/api/auth/logout", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK 