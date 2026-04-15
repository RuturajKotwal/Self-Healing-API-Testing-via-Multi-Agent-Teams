**Diagnosis:** The test `test_get_users` failed because the response from the API is not a list, but rather an object containing a `data` field that is a list. According to the new OpenAPI schema, the response for the `GET /api/v2/users` endpoint is expected to return an object with a `data` field that contains the list of users, along with a `total_count` field. The test is incorrectly asserting that the response is a list instead of checking for the correct structure.

**Setup Fixes (POST/PUT/etc):** The setup for seeding the database is correct, as it uses the required fields from the new schema. However, ensure that the headers are consistently applied to all requests.

**Target Fixes (Main Assertion):** The main assertion needs to be updated to check that the response is an object and that the `data` field is a list. The test should also assert the `total_count` field to ensure it matches the expected number of users.

**Actionable Steps for Coder:**
1. Update the assertion for the response in `test_get_users` to check that the response is a dictionary and contains the `data` key.
2. Change the assertion to check that `data` is a list and that `total_count` matches the expected number of users.
3. Ensure that the headers are included in the `client.post` call when seeding the database.
4. Update the assertions to reflect the new structure of the response.

Here is the modified `test_get_users` function:

```python
def test_get_users():
    # Setup: Seed the database with one user
    client.post("/api/v2/users", json={
        "first_name": "Alice",
        "last_name": "Smith",
        "contact_email": "alice@test.com",
        "role": "customer"
    }, headers={"x-api-version": "0.1.0"})
    
    response = client.get("/api/v2/users?limit=1&offset=0", headers={"x-api-version": "0.1.0"})
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)  # Check that the response is a dictionary
    assert "data" in data  # Check that 'data' key exists
    assert isinstance(data["data"], list)  # Check that 'data' is a list
    assert len(data["data"]) == 1  # Check that the length of the list is 1
    assert data["data"][0]["first_name"] == "Alice"
    assert data["data"][0]["last_name"] == "Smith"
    assert data["data"][0]["contact_email"] == "alice@test.com"
    assert "role" in data["data"][0]  # Check that 'role' is present
```

By following these steps, the test should correctly validate the response structure according to the new OpenAPI schema.