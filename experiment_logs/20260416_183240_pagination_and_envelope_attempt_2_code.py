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
        "role": "customer"
    }
    response = client.post("/api/v2/users", json=payload, headers={"x-api-version": "1.0"})
    
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "Agent"
    assert data["contact_email"] == "agent@test.com"
    assert "user_id" in data

def test_get_users():
    # Setup: Seed the database with one user
    client.post("/api/v2/users", json={"first_name": "Alice", "last_name": "Wonderland", "contact_email": "alice@test.com", "role": "customer"}, headers={"x-api-version": "1.0"})
    
    response = client.get("/api/v2/users?limit=10&offset=0", headers={"x-api-version": "1.0"})
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["first_name"] == "Alice"

def test_get_user_by_id():
    # Setup: Create a user and grab their generated ID
    create_resp = client.post("/api/v2/users", json={"first_name": "Bob", "last_name": "Builder", "contact_email": "bob@test.com", "role": "customer"}, headers={"x-api-version": "1.0"})
    user_id = create_resp.json()["user_id"]

    # Test the fetch
    response = client.get(f"/api/v2/users/{user_id}", headers={"x-api-version": "1.0"})
    assert response.status_code == 200
    
    data = response.json()
    assert data["first_name"] == "Bob"
    assert data["user_id"] == user_id

def test_get_user_not_found():
    response = client.get("/api/v2/users/999", headers={"x-api-version": "1.0"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}