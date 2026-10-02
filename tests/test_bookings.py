def test_create_booking(client):
    # 1. Setup: Create user, get token, create test, create centre
    client.post("/auth/signup", json={"name": "User", "email": "user@example.com", "password": "pwd"})
    token = client.post("/auth/login", data={"username": "user@example.com", "password": "pwd"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    test_res = client.post("/tests", json={"name": "Blood Test", "price": 500}, headers=headers)
    centre_res = client.post("/centres", json={"name": "Clinic", "location": "Pune", "test_ids": [test_res.json()["id"]]}, headers=headers)
    
    # 2. Test: Create the booking
    booking_res = client.post(
        "/bookings/",
        json={
            "centre_id": centre_res.json()["id"],
            "test_id": test_res.json()["id"],
            "appointment_time": "2026-12-01T10:00:00Z"
        },
        headers=headers
    )
    
    assert booking_res.status_code == 201
    assert booking_res.json()["amount"] == "500.00"
    assert booking_res.json()["status"] == "PENDING"