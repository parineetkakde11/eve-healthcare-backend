def test_signup_success(client):
    response = client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert "id" in response.json()

def test_login_success(client):
    # Setup: Create the user first
    client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Test: Log in with correct credentials
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"