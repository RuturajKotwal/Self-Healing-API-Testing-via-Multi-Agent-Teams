import pytest
from fastapi.testclient import TestClient
from main_v2 import app, fake_db

client = TestClient(app)

# Reset the in-memory database before every test to ensure isolation
@pytest.fixture(autouse=True)
def reset_db():
    fake_db.clear()
    import main_v2
    main_v2.current_id = 1
    yield

def test_create_user():
    payload = {"first_name": "Test", "last_name": "Agent", "contact_email": "agent@test.com", "role": "customer"}
    response = client.post("/api/v2/users", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "Agent"
    assert data["contact_email"] == "agent@test.com"
    assert "id" in data

def test_get_users():
    # Setup: Seed the database with one user
    client.post("/api/v2/users", json={"first_name": "Alice", "last_name": "Smith", "contact_email": "alice@test.com", "role": "customer"})
    
    response = client.get("/api/v2/users")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["first_name"] == "Alice"

def test_get_user_by_id():
    # Setup: Create a user and grab their generated ID
    create_resp = client.post("/api/v2/users", json={"first_name": "Bob", "last_name": "Brown", "contact_email": "bob@test.com", "role": "customer"})
    user_id = create_resp.json()["id"]

    # Test the fetch
    response = client.get(f"/api/v2/users/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["first_name"] == "Bob"
    assert data["id"] == user_id

def test_get_user_not_found():
    # Setup: Create a user to ensure the database is not empty
    client.post("/api/v2/users", json={
        "first_name": "Test",
        "last_name": "User",
        "contact_email": "test.user@example.com",
        "role": "customer"
    }, headers={"x-api-version": "0.1.0"})
    
    user_id = "123e4567-e89b-12d3-a456-426614174000"  # Use a valid UUID that does not exist
    headers = {"x-api-version": "0.1.0"}  # Add the required header
    response = client.get(f"/api/v2/users/{user_id}", headers=headers)  # Include headers in the request
    assert response.status_code == 200  # Expect 200 OK
    
    response_data = response.json()
    assert response_data["success"] is False
    assert response_data["error"] == "User not found"
    assert response_data["data"] is None