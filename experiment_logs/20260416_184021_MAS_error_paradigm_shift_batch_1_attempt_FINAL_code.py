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
        "role": "admin"
    }
    response = client.post("/users", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "Agent"
    assert data["contact_email"] == "agent@test.com"
    assert data["role"] == "admin"
    assert "id" in data

def test_get_users():
    # Setup: Seed the database with one user
    client.post("/users", json={"first_name": "Alice", "last_name": "Smith", "contact_email": "alice@test.com", "role": "user"})
    
    response = client.get("/users")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["first_name"] == "Alice"

def test_get_user_by_id():
    # Setup: Create a user and grab their generated ID
    create_resp = client.post("/users", json={"first_name": "Bob", "last_name": "Brown", "contact_email": "bob@test.com", "role": "user"})
    user_id = create_resp.json()["id"]

    # Test the fetch
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["first_name"] == "Bob"
    assert data["id"] == user_id

def test_get_user_not_found():
    # Use a valid UUID for the user_id
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    # Add the required header
    headers = {"x-api-version": "0.1.0"}
    response = client.get(f"/users/{user_id}", headers=headers)
    # Expect a 404 Not Found status code
    assert response.status_code == 404
    # Check for the custom error message
    assert response.json() == {"detail": "User not found"}