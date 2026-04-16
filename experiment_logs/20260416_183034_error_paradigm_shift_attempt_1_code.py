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
    payload = {"username": "test_agent", "email": "agent@test.com"}
    response = client.post("/users", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "test_agent"
    assert data["email"] == "agent@test.com"
    assert "id" in data

def test_get_users():
    # Setup: Seed the database with one user
    client.post("/users", json={"username": "alice", "email": "alice@test.com"})
    
    response = client.get("/users")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["username"] == "alice"

def test_get_user_by_id():
    # Setup: Create a user and grab their generated ID
    create_resp = client.post("/users", json={"username": "bob", "email": "bob@test.com"})
    user_id = create_resp.json()["id"]

    # Test the fetch
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "bob"
    assert data["id"] == user_id

def test_get_user_not_found():
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}