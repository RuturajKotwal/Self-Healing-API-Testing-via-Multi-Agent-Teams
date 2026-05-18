# Agentic Orchestration for Self-Healing Test Suites

**Agentic Orchestration for Self-Healing Test Suites: Evaluating Single and Multi-Agent Workflows using Proprietary Models and Local Open-Source Models**

This repository contains the implementation, experiments, and analysis code for a thesis evaluating self-healing test-suite workflows. The project compares single-agent and multi-agent orchestration strategies that repair broken integration tests against a deliberately changed FastAPI service. Results capture both proprietary LLM behavior and local open-source model evaluation artifacts.

---

## 📌 Project Overview

This work explores how agentic orchestration can automatically repair tests after API schema drift and semantic changes.

- `main.py`: Baseline FastAPI sandbox for the original User Directory API.
- `main_v2.py`: Broken API version with ten intentional taxonomy and contract changes.
- `test_main.py`: Current test suite targeting the broken API.
- `test_main_v1_backup.py`: Backup of the original test suite used to reset experiments.
- `baseline_agent.py`: Single-agent experiment driver using OpenAI to directly patch tests and validate with `pytest`.
- `multi_agent.py`: Multi-agent workflow built with `langgraph` using separate Planner, Coder, and Reviewer agents.

Additional analysis and artifact generation scripts are included for thesis reporting.

---

## 🧠 Key Components

### Broken API Scenario

`main_v2.py` intentionally introduces the following API changes:

- global route prefixing (`/api/v2`)
- mandatory `X-API-Version` headers
- paginated and enveloped responses
- UUID-based path parameter changes
- renamed payload and response fields
- enum validation requirements
- custom error paradigm returning `200 OK` for not-found cases

These changes create a controlled environment for evaluating self-healing test workflows.

### Single-Agent Repair

`baseline_agent.py` performs a published-style single-agent experiment:

- reads the broken test file
- fetches the current OpenAPI schema
- prompts a proprietary model to rewrite failing tests
- runs `pytest` to validate the patch
- logs results and artifacts to `experiment_logs/` and `thesis_results.csv`

### Multi-Agent Repair

`multi_agent.py` composes a Planner/Coder/Reviewer graph with `langgraph`:

- `planner_node` generates a structured repair strategy
- `coder_node` rewrites test code from the planner blueprint
- `reviewer_node` executes the targeted Pytest run
- dynamic routing ensures retry loops until success or exhaustion

This architecture is designed to evaluate whether agent decomposition improves self-healing reliability.

---

## 📁 Repository Structure

- `main.py` - FastAPI V1 user directory sandbox
- `main_v2.py` - Broken V2 API with compatibility changes
- `test_main.py` - Current test suite under repair
- `test_main_v1_backup.py` - Original test suite backup
- `baseline_agent.py` - Single-agent experiment driver
- `multi_agent.py` - Multi-agent orchestration experiment driver
- `analyze_results.py` - Results analysis utilities
- `generate_final.py`, `generate_moe_charts.py`, `generate_thesis_charts.py` - Chart and thesis artifact generation
- `requirements.txt` - Python dependencies
- `thesis_results*.csv` - Experiment result logs
- `local_models_results.csv` - Local open-source model evaluation results
- `Figure_*.png` - Thesis figures and benchmark visuals
- `thesis_data_tables_*.md` - Markdown data tables for reporting

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set OpenAI Credentials

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Broken API Server

```bash
uvicorn main_v2:app --reload
```

The OpenAPI schema is available at `http://127.0.0.1:8000/openapi.json`.

### 4. Run Experiments

#### Single-agent experiment

```bash
python baseline_agent.py
```

#### Multi-agent experiment

```bash
python multi_agent.py
```

Both drivers reset `test_main.py` from `test_main_v1_backup.py` before each experiment and record results to `thesis_results.csv`.

---

## 📊 Results and Analysis

The repository includes multiple experiment outcome artifacts:

- `thesis_results.csv` - combined experiment results
- `thesis_results_gpt4_1.csv`, `thesis_results_gpt4omini.csv` - model-specific result slices
- `thesis_results_llama_8b.csv`, `thesis_results_qwen_32b.csv`, `thesis_results_qwen_7b.csv`, `thesis_results_deepseek_16b.csv` - local/open-source model result comparisons
- `local_models_results.csv` - local model performance summary
- `Figure_*.png` - visualization assets for the thesis
- `thesis_data_tables_*.md` - formatted tables for inclusion in the thesis

Use `generate_moe_charts.py`, `generate_thesis_charts.py`, and `generate_final.py` to reproduce or extend visual analysis.

---

## 🧪 Notes

- `test_main.py` currently contains the legacy test expectations; the broken API intentionally violates those expectations to drive the self-healing experiments.
- `baseline_agent.py` and `multi_agent.py` depend on OpenAI GPT model access via `OPENAI_API_KEY`.
- Local open-source model results are captured in CSV artifacts rather than in the primary Python drivers.

---

## 📚 Thesis Context

This repository supports the thesis investigation into:

- how agentic orchestration can repair test suites automatically
- whether decomposition into planning, coding, and reviewing agents improves robustness
- the trade-offs between proprietary LLMs and local open-source models
- evaluation across varying schema change categories, from medium to hard

---

## ⚙️ Recommended Workflow

1. Start the broken API server.
2. Reset `test_main.py` from `test_main_v1_backup.py` if needed.
3. Run `baseline_agent.py` or `multi_agent.py`.
4. Inspect `experiment_logs/` and the generated CSV files.
5. Use analysis scripts to produce charts and thesis-ready tables.

---

## License

This repository is provided for academic and thesis research purposes.
