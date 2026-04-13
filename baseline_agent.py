import subprocess
import json
import csv
import os
import httpx
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# --- CONFIGURATION ---
# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_ATTEMPTS = 3
RESULTS_FILE = "thesis_results.csv"

def init_csv():
    """Creates the CSV and writes headers if it doesn't exist."""
    try:
        with open(RESULTS_FILE, 'x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "architecture", "change_category", 
                "change_name", "iteration_count", "success", 
                "total_tokens", "failure_reason"
            ])
    except FileExistsError:
        pass # File already exists

def log_result(architecture, category, name, iterations, success, tokens, reason=""):
    """Appends a single experiment run to the CSV."""
    with open(RESULTS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(), architecture, category, 
            name, iterations, success, tokens, reason
        ])

def run_tests():
    """Runs pytest and returns (success_boolean, combined_logs)."""
    result = subprocess.run(["pytest", "test_main.py"], capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr

def get_openapi_schema():
    """Fetches the V2 OpenAPI schema from the running FastAPI instance."""
    try:
        # Ensure your V2 API is running on port 8000
        response = httpx.get("http://127.0.0.1:8000/openapi.json")
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        return f"Error fetching schema: {e}"

def baseline_loop(change_category, change_name):
    print(f"Starting baseline experiment for: {change_name} ({change_category})")
    total_tokens_used = 0
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n--- Attempt {attempt} ---")
        success, logs = run_tests()
        
        if success:
            print("✅ Tests passed! The agent successfully healed the code.")
            log_result("single_agent", change_category, change_name, attempt, True, total_tokens_used)
            return
            
        print("❌ Tests failed. Asking LLM for a fix...")
        
        # Read the current broken test code
        with open("test_main.py", "r") as f:
            current_code = f.read()
            
        schema = get_openapi_schema()
        
        # Construct the prompt
        prompt = f"""
        You are an expert QA engineer. The integration tests are failing because the API has been updated.
        
        Here is the new OpenAPI schema for the API:
        ```json
        {schema}
        ```
        
        Here is the current test code:
        ```python
        {current_code}
        ```
        
        Here are the pytest error logs:
        ```text
        {logs}
        ```
        
        Rewrite the test code to make it pass. Return ONLY the fully updated python code inside ```python ``` blocks. Do not include any other text.
        """
        
        # Make the live OpenAI call
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Using 4o-mini for rapid, cost-effective baseline testing
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        # Extract token usage and add to running total
        tokens = response.usage.total_tokens
        total_tokens_used += tokens
        print(f"Token Usage this attempt: {tokens}")
        
        # Extract code and clean markdown formatting
        new_code = response.choices[0].message.content
        new_code = new_code.replace("```python\n", "").replace("```python", "").replace("```", "").strip()
        
        # Overwrite the test file with the LLM's proposed fix
        with open("test_main.py", "w") as f:
            f.write(new_code)
            
    # If the loop completes without returning, the agent failed
    if not success:
        print("🚨 Baseline agent failed to heal the tests after max attempts.")
        # Grab the last 200 characters of the error log to record the final failure state
        final_error = logs[-200:].replace("\n", " ") 
        log_result("single_agent", change_category, change_name, MAX_ATTEMPTS, False, total_tokens_used, final_error)

if __name__ == "__main__":
    init_csv()
    
    # Execution Example:
    # 1. Start your main_v2.py in a separate terminal (`uvicorn main_v2:app --reload`)
    # 2. Ensure test_main.py is in a failing state.
    # 3. Run this script.
    
    baseline_loop(change_category="easy", change_name="route_prefixing")