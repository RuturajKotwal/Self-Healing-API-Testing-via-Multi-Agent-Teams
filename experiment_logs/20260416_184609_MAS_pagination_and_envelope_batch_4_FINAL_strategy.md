**Diagnosis:** The test `test_get_users` failed because the response from the API is not a list, but rather an object containing a `data` field that is a list of users and a `total_count` field. This structure does not match the expectation in the test that the response should be a list. The OpenAPI schema indicates that the response for the GET request to `/api/v2/users` should return an object, not a list.

**Setup Fixes (POST/PUT/etc):** The setup for seeding the database is correct, as it uses the required fields from the new schema. However, ensure that the headers are consistently applied to all requests.

**Target Fixes (Main Assertion):** The main assertion needs to be updated to reflect the new response structure. Instead of checking if `data` is a list, the test should check if `data['data']` is a list and also verify the `total_count` field.

**Actionable Steps for Coder:**
1. In the `test_get_users` function, after the line where the user is created, ensure that the headers are included in the `client.post` call:
   ```python
   headers={"x-api-version": "0.1.0"}
   ```

2. Update the assertion for the response in the `test_get_users` function:
   - Change the line:
     ```python
     assert isinstance(data, list)
     ```
     to:
     ```python
     assert isinstance(data['data'], list)
     ```

3. Add an assertion to check the `total_count` field in the response:
   ```python
   assert data['total_count'] == 1
   ```

4. Update the final assertions to access the user data correctly:
   - Change:
     ```python
     assert len(data) == 1
     assert data[0]["first_name"] == "alice"
     assert data[0]["last_name"] == "Smith"
     assert data[0]["contact_email"] == "alice@test.com"
     assert data[0]["role"] == "customer"
     ```
     to:
     ```python
     assert len(data['data']) == 1
     assert data['data'][0]["first_name"] == "alice"
     assert data['data'][0]["last_name"] == "Smith"
     assert data['data'][0]["contact_email"] == "alice@test.com"
     assert data['data'][0]["role"] == "customer"
     ```

5. Ensure that the `x-api-version` header is consistently used in all requests, including the `client.get` call in `test_get_users`.

By following these steps, the test should align with the new OpenAPI schema and pass successfully.