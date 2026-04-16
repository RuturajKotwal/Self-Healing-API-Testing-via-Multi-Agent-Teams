from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv
import httpx
import shutil
import json
import csv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RESULTS_FILE = "thesis_results.csv"
LOGS_DIR = "experiment_logs"

# --- EXPERIMENT AUTOMATION ---
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

# --- 1. THE GRAPH STATE ---
class AgentState(TypedDict):
    # Inputs & Context
    test_function: str          # e.g., "test_get_users"
    v2_schema: str              # The OpenAPI JSON
    current_code: str           # The broken test_main.py code
    
    # Agent Outputs
    planner_strategy: str       # The Markdown blueprint written by the Planner
    proposed_code: str          # The Python code written by the Coder
    pytest_logs: str            # The stderr from the Reviewer
    
    # Telemetry (Crucial for the Thesis Data)
    loop_count: int             # How many times have we run Pytest?
    total_tokens: int           # Accumulated token cost across all agents
    llm_calls: int              # Total number of API requests made
    success: bool               # Did it pass?

# --- LOGGING ---
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

# --- 2. THE NODES ---

def planner_node(state: AgentState):
    """Analyzes the schema and test code to formulate a precise repair strategy."""
    print("🧠 [PLANNER] Analyzing schema and drafting strategy...")
    
    error_context = f"PREVIOUS TEST FAILURES TO FIX:\n{state.get('pytest_logs', 'None')}" if state.get('pytest_logs') else "This is the first attempt."
    
    prompt = f"""
    You are an elite QA Architect AI. Your job is to analyze an OpenAPI schema and write a strict technical blueprint to fix a broken integration test.
    
    TARGET TEST TO FIX: {state['test_function']}
    
    === NEW OPENAPI SCHEMA ===
    {state['v2_schema']}
    
    === CURRENT BROKEN TEST CODE ===
    {state['current_code']}
    
    === {error_context} ===
    
    INSTRUCTIONS:
    Write a highly specific, step-by-step technical blueprint for the Coder agent to implement.
    
    CRITICAL CONSTRAINTS & THE INFALLIBILITY RULE:
    1. THE API IS INFALLIBLE: You MUST assume the OpenAPI schema and the API's current behavior are 100% correct and intentional. 
    2. DEFY REST CONVENTIONS IF NECESSARY: If the API returns a 200 OK for an error state (e.g., User Not Found), DO NOT assume the API is broken. The API developers did this on purpose. You MUST instruct the coder to rewrite the test to assert `status_code == 200` and check the JSON payload for the custom error message.
    3. AVOID TUNNEL VISION: Integration tests often have "Setup" steps. You MUST analyze and fix EVERY single `client` call in the test function, line-by-line.
    4. PAYLOAD MAPPING: If the test setup uses old fields (e.g., 'username'), you MUST instruct the coder to replace them with the new required fields from the schema (e.g., 'first_name', 'last_name', 'role').
    5. HEADERS: Explicitly instruct the coder to add required headers to ALL `client` requests.
    6. SEMANTIC PRESERVATION: You MUST preserve the original business intent of the test. Look at the test name (e.g., 'not_found'). If the API requires a UUID, DO NOT just assert a 422 validation error for a bad integer like '999'. You must instruct the coder to use a valid, fake UUID (e.g., '123e4567-e89b-12d3-a456-426614174000') so the test successfully reaches the actual 'Not Found' business logic (which may be a 200 OK with a custom error payload).
    
    FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
    **Diagnosis:** [Explain why the test failed based strictly on how the test violates the NEW schema]
    **Setup Fixes (POST/PUT/etc):** [Exact instructions for fixing database seeding steps]
    **Target Fixes (Main Assertion):** [Exact instructions for fixing the main API call and assertions. If the status code changed, explicitly state the new expected status code.]
    **Actionable Steps for Coder:** [Numbered list of exact, chronological changes to make to the script]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0 # ZERO temperature for strict analytical determinism
    )
    
    strategy = response.choices[0].message.content
    tokens = response.usage.total_tokens
    
    return {
        "planner_strategy": strategy,
        "total_tokens": state.get("total_tokens", 0) + tokens,
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def coder_node(state: AgentState):
    """Translates the Planner's strategy into Python test code."""
    print("💻 [CODER] Writing code based on strategy...")
    
    prompt = f"""
    You are an expert Python Test Engineer. 
    
    === CURRENT TEST CODE ===
    ```python
    {state['current_code']}
    ```
    
    === ARCHITECT'S BLUEPRINT ===
    {state['planner_strategy']}
    
    === PREVIOUS ERRORS (IF ANY) ===
    {state.get('pytest_logs', 'None')}
    
    TASK: 
    Rewrite the test code to implement the Architect's blueprint PERFECTLY. 
    If there are previous errors (like syntax errors or missing imports), fix them while applying the blueprint.
    
    Return ONLY the fully updated python code inside ```python ``` blocks.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    code = response.choices[0].message.content
    code = code.replace("```python\n", "").replace("```python", "").replace("```", "").strip()
    tokens = response.usage.total_tokens
    
    return {
        "proposed_code": code,
        "total_tokens": state["total_tokens"] + tokens,
        "llm_calls": state["llm_calls"] + 1
    }

def reviewer_node(state: AgentState):
    """Executes the Pytest suite and returns the outcome."""
    print("🔬 [REVIEWER] Executing test suite...")
    
    # Overwrite the test file with the Coder's proposed code
    with open("test_main.py", "w", encoding='utf-8') as f:
        f.write(state["proposed_code"])
        
    cmd = ["pytest", f"test_main.py::{state['test_function']}", "-v"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    success = (result.returncode == 0)
    logs = result.stdout + result.stderr
    
    # Update the loop count here to prevent infinite loops
    current_loops = state.get("loop_count", 0) + 1
    
    return {
        "pytest_logs": logs,
        "success": success,
        "loop_count": current_loops,
        "current_code": state["proposed_code"] # Update current code for the next loop
    }

def router_node(state: AgentState):
    """Decides if the graph should loop back to the Planner or End."""
    if state["success"]:
        print("✅ [ROUTER] Tests Passed! Terminating graph.")
        return END
    
    if state["loop_count"] >= 3: # Max 3 execution attempts
        print("🚨 [ROUTER] Max loops reached. Terminating graph with failure.")
        return END
        
    print("❌ [ROUTER] Tests failed. Routing back to Planner for a new strategy.")
    return "planner"

# --- 3. COMPILE THE GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("coder", coder_node)
workflow.add_node("reviewer", reviewer_node)

# Define the flow
workflow.set_entry_point("planner")
workflow.add_edge("planner", "coder")
workflow.add_edge("coder", "reviewer")
workflow.add_conditional_edges("reviewer", router_node)

# Compile into an executable app
multi_agent_app = workflow.compile()

def get_openapi_schema():
    """Fetches the V2 OpenAPI schema from the running FastAPI instance."""
    try:
        response = httpx.get("http://127.0.0.1:8000/openapi.json")
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        return f"Error fetching schema: {e}"

if __name__ == "__main__":
    init_logging() 
    schema = get_openapi_schema()

    # Run the experiment 5 times
    for run_number in range(1, 6):
        print(f"\n{'='*60}")
        print(f"🌟 MULTI-AGENT EXPERIMENT - BATCH {run_number} OF 5 🌟")
        print(f"{'='*60}")
        
        for experiment in EXPERIMENT_MATRIX:
            target_test = experiment["test_function"]
            change_category = experiment["change_category"]
            change_name = experiment["change_name"]
            
            try:
                shutil.copy("test_main_v1_backup.py", "test_main.py")
            except FileNotFoundError:
                print("🚨 ERROR: Backup file not found!")
                exit(1)

            with open("test_main.py", "r", encoding="utf-8") as f:
                broken_code = f.read()
                
            run_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_MAS_{change_name}_batch_{run_number}"

            initial_state = {
                "test_function": target_test,
                "v2_schema": schema,
                "current_code": broken_code,
                "loop_count": 0,
                "total_tokens": 0,
                "llm_calls": 0,
                "success": False
            }

            final_state = multi_agent_app.invoke(initial_state)
            
            save_artifact(run_id, "FINAL", final_state['current_code'], final_state.get('pytest_logs', ''))
            strategy_path = os.path.join(LOGS_DIR, f"{run_id}_FINAL_strategy.md")
            with open(strategy_path, "w", encoding='utf-8') as f:
                f.write(final_state.get('planner_strategy', 'No strategy recorded.'))

            final_error = final_state.get('pytest_logs', '')[-200:].replace("\n", " ") if not final_state['success'] else ""
            
            log_result_csv(
                run_id=run_id,
                architecture="multi_agent",
                category=change_category,
                name=change_name,
                iterations=final_state['llm_calls'],
                success=final_state['success'],
                tokens=final_state['total_tokens'],
                reason=final_error
            )