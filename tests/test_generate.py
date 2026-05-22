import pytest
from unittest.mock import patch
from app.models.user import User

def test_create_clipping(client, db):
    # First sign up
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "clipper@example.com",
            "password": "password123",
            "firstName": "Clip",
            "lastName": "Maker",
            "acceptTerms": True
        }
    )
    # Activate user
    user = db.query(User).filter(User.email == "clipper@example.com").first()
    user.is_active = True
    db.commit()

    # Login to get token
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "clipper@example.com",
            "password": "password123"
        }
    )
    token = login_res.json()["data"]["token"]
    
    # Mock background_tasks.add_task to avoid running the playwright rendering engine in unit test
    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        response = client.post(
            "/api/v1/generate/",
            json={
                "headline": "Test Headline",
                "articleContent": "This is a test article content for newspaper rendering.",
                "language": "en",
                "tone": "formal",
                "templateId": "bharath_reporter",
                "publicationName": "Bharath Reporter",
                "publicationDate": "Tuesday, May 19, 2026",
                "layoutColumns": 3,
                "fontFamily": "playfair"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["headline"] == "Test Headline"
        assert data["data"]["status"] == "processing"
        
        # Verify background task was added
        mock_add_task.assert_called_once()

def test_get_all_clippings(client, db):
    # Signup
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "clipper2@example.com",
            "password": "password123",
            "firstName": "Clip",
            "lastName": "Maker",
            "acceptTerms": True
        }
    )
    # Activate user
    user = db.query(User).filter(User.email == "clipper2@example.com").first()
    user.is_active = True
    db.commit()

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "clipper2@example.com",
            "password": "password123"
        }
    )
    token = login_res.json()["data"]["token"]
    
    # Create clipping
    with patch("fastapi.BackgroundTasks.add_task"):
        client.post(
            "/api/v1/generate/",
            json={
                "headline": "Headline 1",
                "articleContent": "Content 1",
                "templateId": "bharath_reporter",
                "publicationName": "Bharath Reporter",
                "publicationDate": "Tuesday, May 19, 2026"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
    # Get clippings
    response = client.get(
        "/api/v1/generate/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) == 1
    assert data["data"]["items"][0]["headline"] == "Headline 1"
