**Diagnosis:** The `test_create_user` function is failing because the payload being sent to the API does not conform to the new OpenAPI schema. The schema requires fields `first_name`, `last_name`, `contact_email`, and `role`, but the test is using `username` and `email`, which are not defined in the new schema. Additionally, the required header `x-api-version` is missing from the request.

**Setup Fixes (POST/PUT/etc):** The setup for creating a user must be updated to include the correct fields as per the new schema. The test should also include the required header `x-api-version` in the request.

**Target Fixes (Main Assertion):** The main API call should be updated to include the correct payload structure. The expected response status code remains `201`, but the assertions should check for the correct fields in the response based on the new schema.

**Actionable Steps for Coder:**
1. Update the `payload` in the `test_create_user` function to include the required fields from the new schema:
   ```python
   payload = {
       "first_name": "Test",
       "last_name": "Agent",
       "contact_email": "agent@test.com",
       "role": "customer"  # or "admin", depending on the test case
   }
   ```
2. Add the required header `x-api-version` to the `client.post` call:
   ```python
   headers = {"x-api-version": "0.1.0"}
   response = client.post("/api/v2/users", json=payload, headers=headers)
   ```
3. Update the assertions to check for the correct fields in the response:
   ```python
   assert data["first_name"] == "Test"
   assert data["last_name"] == "Agent"
   assert data["contact_email"] == "agent@test.com"
   assert "user_id" in data  # Check for the user_id instead of id
   ```

4. Ensure that the endpoint in the `client.post` call is updated to match the new API path:
   ```python
   response = client.post("/api/v2/users", json=payload, headers=headers)
   ```

5. Review and update any other tests that may also be using the old payload structure or missing headers, ensuring they conform to the new schema as well.