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
        You are an expert QA engineer. The integration tests are failing because the API has been updated.
        
        Here is the new OpenAPI schema for the API:
        ```json
        {schema}
        ```
        
        Here is the current test code:
        ```python
        {current_code}
        ```
        
        Here are the pytest error logs for the specific failing test:
        ```text
        {logs}
        ```
        
        Rewrite the test code to make it pass. Return ONLY the fully updated python code inside ```python ``` blocks. Do not include any other text.
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
        new_code = response.choices[0].message.content
        new_code = new_code.replace("```python\n", "").replace("```python", "").replace("```", "").strip()
        
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