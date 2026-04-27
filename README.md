# Overview
This the replication package for an empirical study on evaluating multi-agent systems (MAS) for code generation tasks.

## Repository Structure

```text
MASEvaluation-git/
├── multiAgent/              # Multi-agent code generation framework
│   ├── agents/              # Agent implementations, such as planner, programmer, reviewer, and tester
│   ├── graphs/              # Workflow definitions for different MAS collaboration patterns
│   ├── prompt/              # Prompt templates used by different agents
│   ├── state/               # Shared state schema for graph-based workflows
│   ├── config/              # Runtime configuration
│   ├── Task/                # Task files used by the multi-agent runner
│   ├── run.py               # Example script for running a single workflow
│   └── run_batch.py         # Batch runner for benchmark tasks
│
├── Task/
│   └── feature.json         # Task descriptions and feature-level evaluation criteria
│
├── LLMasJudge/              # LLM-as-a-judge evaluation module
│   ├── judge.py             # Main judging script
│   ├── judge_prompt.py      # Prompt template for feature-level judging
│   └── calcFeature.py       # Aggregation script for feature completion results
│
├── Pylint/                  # Static code quality analysis scripts
│   ├── AnalysisPylint.py    # Pylint and Radon analysis
│   ├── LoC.py               # Lines-of-code analysis
│   └── OuputResult.py       # Result processing script
│
├── RQ3/
│   └── Time_Token.py        # Runtime and token usage summarization
│
└── Logs/                    # Experimental logs
```

# Environment Setup

## 1. Clone the Repository

```bash
git clone https://github.com/hapiiiiGit/MASEvaluation-git.git
cd MASEvaluation-git
```

## 2. Create a Python Environment

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows
```

## 3. Install Dependencies

The repository currently does not provide a `requirements.txt` file. The following packages are required by the main experimental scripts:

```bash
pip install openai langgraph pandas openpyxl pylint radon
```

Depending on the model provider and local execution environment, additional packages may be required.

## Configuration

The main configuration file is:

```text
multiAgent/config/setting.py
```

Experiments can be configured through environment variables.

| Variable | Description | Example |
|---|---|---|
| `MODEL_NAME` | Model used by the agents | `gpt-4o-mini` |
| `BASE_URL` | Base URL of the model API provider | `https://api.openai.com/v1` |
| `OPENAI_API_KEY` | API key for the model provider | `your_api_key` |
| `MODEL_TEMPERATURE` | Sampling temperature | `0.0` |
| `MAX_ITERATIONS` | Maximum number of revision iterations | `4` |
| `PROGRAMMER_MODE` | Optional programmer mode setting | `default` |
| `GRAPH_NAME` | Selected MAS workflow | `programmer_reviewer` |
| `TASK_FILE` | Path to the task file | `Task/pro-70.txt` |
| `OUTPUT_ROOT` | Root directory for experimental outputs | `outputs/runs` |
| `MAX_RETRIES` | Maximum retry count for failed tasks | `3` |
| `RETRY_WAIT_SECONDS` | Waiting time between retries | `5` |
