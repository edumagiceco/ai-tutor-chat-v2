import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


def test_signup(client: TestClient, db: Session):
    """Test user signup."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "newpassword123",
            "name": "New User",
            "institution": "Test Institution"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data
    
    # Check user was created in database
    user = db.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None
    assert user.name == "New User"


def test_signup_duplicate_email(client: TestClient, test_user: User):
    """Test signup with duplicate email."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": test_user.email,
            "password": "anotherpassword123",
            "name": "Another User",
            "institution": "Test Institution"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login(client: TestClient, test_user: User):
    """Test user login."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_user: User):
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_nonexistent_user(client: TestClient):
    """Test login with nonexistent user."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "anypassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_get_current_user(client: TestClient, auth_headers: dict):
    """Test getting current user info."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert data["role"] == "user"


def test_get_current_user_unauthorized(client: TestClient):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_admin_access_control(client: TestClient, auth_headers: dict, admin_auth_headers: dict):
    """Test admin access control."""
    # Regular user should not access admin endpoints
    response = client.get("/api/v1/admin/stats", headers=auth_headers)
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]
    
    # Admin should access admin endpoints
    response = client.get("/api/v1/admin/stats", headers=admin_auth_headers)
    assert response.status_code == 200