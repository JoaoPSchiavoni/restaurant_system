from fastapi import status

def test_auth_home(client):
    response = client.get("/auth/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Message": "You have accessed the auth route", "auth": False}

def test_create_account(client):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword",
        "active": True,
        "admin": False
    }
    response = client.post("/auth/create_account", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "User successfully registered test@example.com"}

def test_create_account_duplicate(client):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/auth/create_account", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    response_duplicate = client.post("/auth/create_account", json=payload)
    assert response_duplicate.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response_duplicate.json()["detail"]

def test_login_success(client):
    register_payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword"
    }
    client.post("/auth/create_account", json=register_payload)

    login_payload = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"

def test_login_invalid_credentials(client):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_form_success(client):
    register_payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword"
    }
    client.post("/auth/create_account", json=register_payload)

    form_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/auth/login-form", data=form_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" == "Bearer"

def test_refresh_token(client):
    register_payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword"
    }
    client.post("/auth/create_account", json=register_payload)
    
    login_payload = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    login_res = client.post("/auth/login", json=login_payload)
    access_token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/auth/refresh", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
