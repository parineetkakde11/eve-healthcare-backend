def test_payment_and_idempotent_webhook(client):
    # 1. Setup: User, Test, Centre, Booking
    client.post("/auth/signup", json={"name": "User", "email": "user2@example.com", "password": "pwd"})
    token = client.post("/auth/login", data={"username": "user2@example.com", "password": "pwd"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    test_id = client.post("/tests", json={"name": "X-Ray", "price": 1000}, headers=headers).json()["id"]
    centre_id = client.post("/centres", json={"name": "Hospital", "location": "Mumbai", "test_ids": [test_id]}, headers=headers).json()["id"]
    booking_id = client.post("/bookings/", json={"centre_id": centre_id, "test_id": test_id, "appointment_time": "2026-12-01T10:00:00Z"}, headers=headers).json()["id"]
    
    # 2. Test: Initiate Payment
    payment_res = client.post("/payments/", json={"booking_id": booking_id, "simulate_status": "PENDING"}, headers=headers)
    assert payment_res.status_code == 201
    transaction_ref = payment_res.json()["transaction_ref"]
    
    # 3. Test: Fire Webhook
    webhook_payload = {"event_id": "evt_test_123", "transaction_ref": transaction_ref, "status": "SUCCESS"}
    webhook_res_1 = client.post("/payments/webhook/", json=webhook_payload)
    assert webhook_res_1.status_code == 200
    assert webhook_res_1.json()["message"] == "Webhook processed successfully."
    
    # 4. Test: Idempotency (Fire exact same webhook again)
    webhook_res_2 = client.post("/payments/webhook/", json=webhook_payload)
    assert webhook_res_2.status_code == 200
    assert webhook_res_2.json()["message"] == "Idempotent replay: Event already processed."