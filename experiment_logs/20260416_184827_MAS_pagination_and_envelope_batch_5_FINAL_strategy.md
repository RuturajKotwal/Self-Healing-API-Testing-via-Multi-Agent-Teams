**Diagnosis:** The test `test_get_users` failed because the response from the API is not a list, but rather an object containing a `data` field that is a list of users. This discrepancy arises from the new OpenAPI schema, which indicates that the response structure has changed. The test is currently asserting that the response is a list, which is incorrect according to the new schema.

**Setup Fixes (POST/PUT/etc):** The setup for seeding the database is correct, as it uses the required fields from the new schema. However, ensure that the `x-api-version` header is consistently used in all requests.

**Target Fixes (Main Assertion):** The main API call to get users should be updated to correctly access the `data` field in the response. The assertion should check that `data` is a list and that it contains the expected user information.

**Actionable Steps for Coder:**
1. In the `test_get_users` function, after the line where the user is created, ensure that the `x-api-version` header is included in the `client.get` request.
2. Change the assertion that checks the type of `data` to access the `data` field in the response. Update the assertion to check that `data['data']` is a list.
3. Update the assertion for the length of the user list to check `len(data['data'])` instead of `len(data)`.
4. Update the assertions that check the user details to access `data['data'][0]` instead of `data[0]`.

Here is the modified `test_get_users` function:

```python
def test_get_users():
    # Setup: Seed the database with one user
    response = client.post("/api/v2/users", json={"first_name": "Alice", "last_name": "Smith", "contact_email": "alice@test.com", "role": "customer"}, headers={"x-api-version": "2"})
    
    assert response.status_code == 201  # Ensure user creation was successful

    response = client.get("/api/v2/users?limit=10&offset=0", headers={"x-api-version": "2"})
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data['data'], list)  # Check that 'data' is a list
    assert len(data['data']) == 1  # Check that the list contains one user
    assert data['data'][0]["first_name"] == "Alice"
    assert data['data'][0]["last_name"] == "Smith"
    assert data['data'][0]["contact_email"] == "alice@test.com"
    assert data['data'][0]["role"] == "customer"
```

By following these steps, the test should align with the new OpenAPI schema and pass successfully.