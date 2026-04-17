import subprocess
import json
import csv
import os
import httpx
import shutil
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# --- CONFIGURATION ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Enforce a strict limit of 3 API calls and 3 Pytest runs
MAX_ATTEMPTS = 3 
RESULTS_FILE = "thesis_results.csv"
LOGS_DIR = "experiment_logs"

# --- THE EXPERIMENT MATRIX ---
EXPERIMENT_MATRIX = [
    {
        "test_function": "test_get_users",
        "change_category": "medium",
        "change_name": "pagination_and_envelope"
    },
    {
        "test_function": "test_get_user_not_found",
        "change_category": "hard",
        "change_name": "error_paradigm_shift"
    },
    {
        "test_function": "test_create_user",
        "change_category": "hard",
        "change_name": "semantic_split_and_enum"
    }
]

def init_logging():
    """Creates the CSV and the artifact directory if they don't exist."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    try:
        with open(RESULTS_FILE, 'x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "run_id", "timestamp", "architecture", "change_category", 
                "change_name", "llm_calls", "success", 
                "total_tokens", "final_failure_reason"
            ])
    except FileExistsError:
        pass

def log_result_csv(run_id, architecture, category, name, iterations, success, tokens, reason=""):
    """Appends a single experiment run to the CSV."""
    with open(RESULTS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            run_id, datetime.now().isoformat(), architecture, category, 
            name, iterations, success, tokens, reason
        ])

def save_artifact(run_id, attempt, code, logs):
    """Saves the intermediate code and logs for qualitative analysis."""
    code_path = os.path.join(LOGS_DIR, f"{run_id}_attempt_{attempt}_code.py")
    with open(code_path, "w", encoding='utf-8') as f:
        f.write(code)
        
    log_path = os.path.join(LOGS_DIR, f"{run_id}_attempt_{attempt}_pytest.log")
    with open(log_path, "w", encoding='utf-8') as f:
        f.write(logs)

def run_tests(test_function=None):
    """Runs pytest. If a test_function is provided, it isolates that specific test."""
    cmd = ["pytest", "test_main.py", "-v"]
    if test_function:
        cmd = ["pytest", f"test_main.py::{test_function}", "-v"]
        
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr

def get_openapi_schema():
    """Fetches the V2 OpenAPI schema from the running FastAPI instance."""
    try:
        response = httpx.get("http://127.0.0.1:8000/openapi.json")
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        return f"Error fetching schema: {e}"

def baseline_loop(test_function, change_category, change_name):
    print(f"\n==================================================")
    print(f"🚀 Starting isolated experiment: {change_name} [{change_category.upper()}]")
    print(f"🎯 Target Test: {test_function}")
    print(f"==================================================")
    
    total_tokens_used = 0
    run_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{change_name}"
    
    # Synthetic log to provide context to the LLM on the very first API call
    logs = "Initial state: The test is assumed broken due to API schema changes. Please actively update the test to align with the new OpenAPI schema."
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n--- Attempt {attempt} ---")
        print(f"🤖 Calling LLM for a fix...")
        
        # 1. READ CURRENT BROKEN CODE
        with open("test_main.py", "r", encoding='utf-8') as f:
            current_code = f.read()
            
        # 2. FETCH SCHEMA AND CALL LLM
        schema = get_openapi_schema()
        
        prompt = f"""
        You are an elite Python Test Engineer and QA Architect. The integration tests are failing because the API has been updated.
        
        Here is the new OpenAPI schema for the API:
        ```json
        {schema}
        ```
        
        Here is the current broken test code:
        ```python
        {current_code}
        ```
        
        Here are the pytest error logs for the specific failing test:
        ```text
        {logs}
        ```
        
        TASK:
        Rewrite the test code to make it pass. You must adhere to the following strict architectural rules:

        CRITICAL CONSTRAINTS & THE INFALLIBILITY RULE:
        1. THE API IS INFALLIBLE: You MUST assume the OpenAPI schema and the API's current behavior are 100% correct and intentional. 
        2. DEFY REST CONVENTIONS IF NECESSARY: If the API returns a 200 OK for an error state (e.g., User Not Found), DO NOT assume the API is broken. The API developers did this on purpose. You MUST rewrite the test to assert `status_code == 200` and check the JSON payload for the custom error message.
        3. AVOID TUNNEL VISION: Integration tests often have "Setup" steps. You MUST analyze and fix EVERY single `client` call in the test function, line-by-line.
        4. PAYLOAD MAPPING: If the test setup uses old fields (e.g., 'username'), you MUST replace them with the new required fields from the schema (e.g., 'first_name', 'last_name', 'role').
        5. HEADERS: Explicitly add any newly required headers to ALL `client` requests.
        6. SEMANTIC PRESERVATION: You MUST preserve the original business intent of the test. Look at the test name (e.g., 'not_found'). If the API requires a UUID, DO NOT just assert a 422 validation error for a bad integer like '999'. You must use a valid, fake UUID (e.g., '123e4567-e89b-12d3-a456-426614174000') so the test successfully reaches the actual 'Not Found' business logic.
        
        OUTPUT FORMAT:
        You MUST structure your response in two distinct parts exactly as shown below:

        **Diagnosis:**
        [Write a brief step-by-step analysis of why the test failed based on the NEW schema and formulate a clear strategy to fix it.]

        **Updated Code:**
        ```python
        # Fully updated and complete test_main.py script goes here.
        ```
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        tokens = response.usage.total_tokens
        total_tokens_used += tokens
        print(f"Token Usage this attempt: {tokens}")
        
        # 3. APPLY LLM FIX
        # Extract response
        raw_response = response.choices[0].message.content

        # Parse out just the Python code using basic string splitting
        try:
            new_code = raw_response.split("```python")[1].split("```")[0].strip()
        except IndexError:
            # Fallback if the LLM messes up the markdown formatting
            print("⚠️ Warning: Could not parse standard markdown blocks. Saving raw output.")
            new_code = raw_response

        # Save the new code
        with open("test_main.py", "w", encoding='utf-8') as f:
            f.write(new_code)
            
        # 4. RUN PYTEST ON THE NEW CODE
        print(f"🧪 Running Pytest to validate LLM code...")
        success, logs = run_tests(test_function) 
        
        # 5. SAVE ARTIFACTS
        save_artifact(run_id, attempt, new_code, logs)
        
        if success:
            print(f"✅ Isolated test '{test_function}' passed!")
            # Attempt maps precisely to the number of API calls made
            log_result_csv(run_id, "single_agent", change_category, change_name, attempt, True, total_tokens_used)
            return
            
    # If the loop exhausts all attempts without hitting the 'return' above:
    print(f"🚨 Baseline failed to heal '{test_function}' after {MAX_ATTEMPTS} attempts.")
    final_error_snippet = logs[-200:].replace("\n", " ") if logs else "Unknown error"
    log_result_csv(run_id, "single_agent", change_category, change_name, MAX_ATTEMPTS, False, total_tokens_used, final_error_snippet)

if __name__ == "__main__":
    init_logging()
    
    # Run the experiment 5 times
    for run_number in range(1, 6):
        print(f"\n{'='*60}")
        print(f"🌟 BASELINE EXPERIMENT - BATCH {run_number} OF 5 🌟")
        print(f"{'='*60}")
        
        for experiment in EXPERIMENT_MATRIX:
            print(f"\n[SYSTEM] Resetting test_main.py to V1 state...")
            try:
                shutil.copy("test_main_v1_backup.py", "test_main.py")
            except FileNotFoundError:
                print("🚨 ERROR: 'test_main_v1_backup.py' not found!")
                exit(1)
                
            baseline_loop(
                test_function=experiment["test_function"],
                change_category=experiment["change_category"],
                change_name=experiment["change_name"]
            )