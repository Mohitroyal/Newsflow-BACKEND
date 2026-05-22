import pytest
from app.models.user import User
from app.core import security
from datetime import timedelta

def test_signup(client, db):
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test_user_unique@example.com",
            "password": "password123",
            "firstName": "Mohit",
            "lastName": "Royal",
            "acceptTerms": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Verification link sent! Please check your email."
    
    user = db.query(User).filter(User.email == "test_user_unique@example.com").first()
    assert user is not None
    assert user.is_active is False
    assert user.full_name == "Mohit Royal"

def test_signup_duplicate_email(client, db):
    # First signup
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "firstName": "Mohit",
            "lastName": "Royal",
            "acceptTerms": True
        }
    )
    
    # Activate first user so duplicate is rejected
    user = db.query(User).filter(User.email == "duplicate@example.com").first()
    user.is_active = True
    db.commit()

    # Second signup with same email should now fail
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "firstName": "Mohit",
            "lastName": "Royal",
            "acceptTerms": True
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_signup_unverified_duplicate(client, db):
    # First signup (unverified)
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "unverified_dup@example.com",
            "password": "password123",
            "firstName": "Mohit",
            "lastName": "Royal",
            "acceptTerms": True
        }
    )
    
    # Second signup with same email (still unverified) should succeed and update data
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "unverified_dup@example.com",
            "password": "newpassword123",
            "firstName": "Mohit New",
            "lastName": "Royal New",
            "acceptTerms": True
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    db.expire_all()
    user = db.query(User).filter(User.email == "unverified_dup@example.com").first()
    assert user is not None
    assert user.is_active is False
    assert user.full_name == "Mohit New Royal New"

def test_login(client, db):
    # Signup
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "login_test@example.com",
            "password": "password123",
            "firstName": "Test",
            "lastName": "User",
            "acceptTerms": True
        }
    )
    # Activate user
    user = db.query(User).filter(User.email == "login_test@example.com").first()
    user.is_active = True
    db.commit()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login_test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]
    assert data["data"]["user"]["email"] == "login_test@example.com"

def test_login_unverified(client, db):
    # Signup but do not activate
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "unverified_login@example.com",
            "password": "password123",
            "firstName": "Test",
            "lastName": "User",
            "acceptTerms": True
        }
    )
    
    # Login should fail saying to verify email
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unverified_login@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "verify your email" in response.json()["detail"]

def test_login_incorrect_password(client, db):
    # Signup
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "wrong_password@example.com",
            "password": "password123",
            "firstName": "Test",
            "lastName": "User",
            "acceptTerms": True
        }
    )
    # Activate user
    user = db.query(User).filter(User.email == "wrong_password@example.com").first()
    user.is_active = True
    db.commit()

    # Login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong_password@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]

def test_verify_email(client, db):
    # Register unverified user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "verify_test@example.com",
            "password": "password123",
            "firstName": "Verify",
            "lastName": "Me",
            "acceptTerms": True
        }
    )
    
    token = security.create_access_token(
        subject="verify:verify_test@example.com",
        expires_delta=timedelta(hours=24)
    )
    
    response = client.get(f"/api/v1/auth/verify?token={token}", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert "verified=true" in response.headers["location"]
    
    db.expire_all()
    user = db.query(User).filter(User.email == "verify_test@example.com").first()
    assert user.is_active is True

def test_get_me(client, db):
    # Signup
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "me_test@example.com",
            "password": "password123",
            "firstName": "Me",
            "lastName": "User",
            "acceptTerms": True
        }
    )
    # Activate
    user = db.query(User).filter(User.email == "me_test@example.com").first()
    user.is_active = True
    db.commit()

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "me_test@example.com",
            "password": "password123"
        }
    )
    token = login_res.json()["data"]["token"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "me_test@example.com"
