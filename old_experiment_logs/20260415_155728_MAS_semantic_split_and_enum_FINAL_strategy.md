**Diagnosis:** The `test_create_user` function is failing because it uses outdated field names (`username` and `email`) that do not match the new OpenAPI schema. The schema requires the fields `first_name`, `last_name`, `contact_email`, and `role` in the request payload. Additionally, the required header `x-api-version` is missing from the request, which is necessary for the API to process the request correctly.

**Setup Fixes (POST/PUT/etc):** The database seeding step in the `test_create_user` function must be updated to use the new required fields from the OpenAPI schema. The payload should include `first_name`, `last_name`, `contact_email`, and `role`.

**Target Fixes (Main Assertion):** The main API call in `test_create_user` must be updated to include the required header `x-api-version`. The expected response should still be a 201 status code, but the assertions must check for the new fields in the response payload.

**Actionable Steps for Coder:**
1. Update the `payload` in the `test_create_user` function to include the new required fields:
   ```python
   payload = {
       "first_name": "Test",
       "last_name": "Agent",
       "contact_email": "agent@test.com",
       "role": "customer"  # or "admin", depending on the test case
   }
   ```
2. Add the required header `x-api-version` to the `client.post` request:
   ```python
   response = client.post("/api/v2/users", json=payload, headers={"x-api-version": "0.1.0"})
   ```
3. Update the assertions in the `test_create_user` function to check for the new fields in the response:
   ```python
   assert data["first_name"] == "Test"
   assert data["last_name"] == "Agent"
   assert data["contact_email"] == "agent@test.com"
   assert data["role"] == "customer"  # or "admin", depending on the test case
   assert "user_id" in data
   ```
4. Ensure that the endpoint in the `client.post` call is updated to match the new API path:
   ```python
   response = client.post("/api/v2/users", json=payload, headers={"x-api-version": "0.1.0"})
   ```

By following these steps, the `test_create_user` function will align with the new OpenAPI schema and should pass successfully.