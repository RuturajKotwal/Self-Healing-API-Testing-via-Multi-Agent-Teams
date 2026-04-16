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
    payload = {
        "first_name": "Test",
        "last_name": "Agent",
        "contact_email": "agent@test.com",
        "role": "customer"  # or "admin"
    }
    response = client.post("/api/v2/users", json=payload, headers={"x-api-version": "0.1.0"})
    
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "Agent"
    assert data["contact_email"] == "agent@test.com"
    assert "user_id" in data

def test_get_users():
    # Setup: Seed the database with one user
    payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "contact_email": "alice@test.com",
        "role": "customer"  # or "admin"
    }
    response = client.post("/api/v2/users", json=payload, headers={"x-api-version": "0.1.0"})
    assert response.status_code == 201  # Ensure user creation is successful
    
    response = client.get("/api/v2/users?limit=10&offset=0", headers={"x-api-version": "0.1.0"})
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data  # Check for the presence of 'data' key
    assert isinstance(data["data"], list)  # Check that 'data' is a list
    assert data["total_count"] == 1  # Check that total_count matches the number of users
    
    assert len(data["data"]) == 1  # Ensure there is one user in the list
    assert data["data"][0]["first_name"] == "Alice"
    assert data["data"][0]["last_name"] == "Smith"
    assert data["data"][0]["contact_email"] == "alice@test.com"
    assert "user_id" in data["data"][0]  # Check for the presence of user_id

def test_get_user_by_id():
    # Setup: Create a user and grab their generated ID
    create_resp = client.post("/api/v2/users", json={"first_name": "Bob", "last_name": "Builder", "contact_email": "bob@test.com", "role": "customer"}, headers={"x-api-version": "0.1.0"})
    user_id = create_resp.json()["user_id"]

    # Test the fetch
    response = client.get(f"/api/v2/users/{user_id}", headers={"x-api-version": "0.1.0"})
    assert response.status_code == 200
    
    data = response.json()
    assert data["first_name"] == "Bob"
    assert data["last_name"] == "Builder"
    assert data["user_id"] == user_id

def test_get_user_not_found():
    response = client.get("/api/v2/users/999", headers={"x-api-version": "0.1.0"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}