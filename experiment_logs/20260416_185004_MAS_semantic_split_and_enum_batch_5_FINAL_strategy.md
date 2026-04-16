**Diagnosis:** The `test_create_user` function is failing because it uses outdated field names (`username` and `email`) that do not match the new OpenAPI schema. The schema requires the fields `first_name`, `last_name`, `contact_email`, and `role` in the request payload. Additionally, the required header `x-api-version` is missing from the request, which is mandatory for the API to process the request correctly.

**Setup Fixes (POST/PUT/etc):** The setup for creating a user must be updated to include the correct fields as per the new schema. The payload should be modified to include `first_name`, `last_name`, `contact_email`, and `role`. Furthermore, the request must include the `x-api-version` header with the appropriate value.

**Target Fixes (Main Assertion):** The main API call in `test_create_user` must be updated to reflect the new endpoint `/api/v2/users` instead of `/users`. The assertions should also be updated to check for the correct fields in the response, which are now `user_id`, `first_name`, `last_name`, `contact_email`, and `role`.

**Actionable Steps for Coder:**
1. Update the `test_create_user` function to change the payload to:
   ```python
   payload = {
       "first_name": "Test",
       "last_name": "Agent",
       "contact_email": "agent@test.com",
       "role": "customer"  # or "admin", depending on the test case
   }
   ```
2. Change the API endpoint in the `client.post` call from `"/users"` to `"/api/v2/users"`.
3. Add the required header `x-api-version` to the `client.post` call:
   ```python
   headers = {"x-api-version": "0.1.0"}
   response = client.post("/api/v2/users", json=payload, headers=headers)
   ```
4. Update the assertions to check for the correct fields in the response:
   ```python
   assert data["first_name"] == "Test"
   assert data["last_name"] == "Agent"
   assert data["contact_email"] == "agent@test.com"
   assert "user_id" in data
   ```
5. Ensure that the `test_get_users` and `test_get_user_by_id` functions are also updated to use the correct endpoint and payload structure, if they are using the old fields or endpoints. Specifically, change the endpoint in `client.post` and `client.get` calls to `"/api/v2/users"` and `"/api/v2/users/{user_id}"` respectively, and ensure that the required headers are included in those requests as well.