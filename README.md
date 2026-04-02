# Bug Triage Env

An [OpenEnv](https://github.com/meta-pytorch/OpenEnv)-compatible environment where an AI agent
learns to triage software bug reports across three tasks of increasing difficulty.

Built for the **Meta × PyTorch OpenEnv Hackathon — Round 1**.

---

## What the agent does

Given a raw bug report, the agent must:

| Task | Level | What the agent produces |
|------|-------|------------------------|
| Bug classification | Easy | Category: `UI` / `backend` / `infra` / `security` |
| Classification + priority | Medium | Category + priority (`P0`–`P3`) + one-line reason |
| Full triage + reply | Hard | Category + priority + responsible team + 2-sentence reply |

All responses are JSON strings. Partial credit is awarded — the agent doesn't need to be
perfect to earn a reward.

---

## Action space

The agent sends a single field:

```python
BugTriageAction(response: str)  # a JSON-encoded string
```

**By task level:**

```json
// easy
{"category": "UI"}

// medium
{"category": "backend", "priority": "P1", "reason": "Fails in prod only — likely env config"}

// hard
{"category": "security", "priority": "P0", "team": "security", "reply": "We acknowledge this urgent issue and have escalated it to our security team immediately. We will provide an update within 2 hours."}
```

---

## Observation space

```python
BugTriageObservation(
    task_description: str,  # full prompt + bug report text
    task_level: str,        # "easy" | "medium" | "hard"
    feedback: str,          # human-readable score feedback
    reward: float,          # 0.0 – 1.0
    done: bool,             # True after all 3 tasks
    success: bool           # True if reward >= 0.8
)
```

---

## Reward design

Partial credit per task so the agent can learn gradually:

```
easy   → 1.0 correct category, else 0.0

medium → 0.4  correct category
       + 0.4  correct priority (P0–P3)
       + 0.2  reason present (>10 chars)

hard   → 0.3  correct category
       + 0.3  correct priority
       + 0.2  correct team assignment
       + 0.1  reply length (>30 chars)
       + 0.1  reply tone (apology / urgency keywords)
```

---

## Setup & installation

### Requirements

- Python 3.10+
- Docker Desktop or Docker Engine
- A Hugging Face account + token

### Install locally

```bash
pip install openenv-core
git clone https://huggingface.co/spaces/your-username/bug-triage-env
cd bug-triage-env
pip install -e .
```

### Run the server locally (no Docker)

```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### Run with Docker

```bash
cd server
docker build -t bug-triage-env .
docker run -p 8000:8000 bug-triage-env
```

---

## Quick usage example

```python
from bug_triage_env import BugTriageEnv, BugTriageAction

with BugTriageEnv(base_url="http://localhost:8000").sync() as env:
    # Start a new episode
    obs = env.reset()
    print(obs.observation.task_level)       # "easy"
    print(obs.observation.task_description) # bug report + prompt

    # Agent responds to easy task
    result = env.step(BugTriageAction(response='{"category": "UI"}'))
    print(result.reward)                    # 1.0
    print(result.observation.feedback)     # "Last score: 1.0. Next task level: medium"

    # Agent responds to medium task
    result = env.step(BugTriageAction(
        response='{"category": "backend", "priority": "P1", "reason": "prod only failure"}'
    ))
    print(result.reward)                    # 0.8

    # Agent responds to hard task
    result = env.step(BugTriageAction(
        response='{"category": "security", "priority": "P0", "team": "security", "reply": "We acknowledge this critical issue and are escalating immediately."}'
    ))
    print(result.reward)                    # up to 1.0
    print(result.observation.done)          # True
```

---

## Running inference

Set required environment variables, then run:

```bash
export API_BASE_URL="https://api-inference.huggingface.co/v1"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
export HF_TOKEN="hf_your_token_here"
export HF_SPACE_URL="https://your-username-bug-triage-env.hf.space"

python inference.py
```

Expected output:

```
Episode started — first task: easy
Agent response: {"category": "UI"}
Reward: 1.0 | Feedback: Last score: 1.0. Next task level: medium
...
=== Final scores: [1.0, 0.8, 0.7] | Average: 0.833 ===
```

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_BASE_URL` | Yes | LLM API endpoint (OpenAI-compatible) |
| `MODEL_NAME` | Yes | Model identifier for inference |
| `HF_TOKEN` | Yes | Hugging Face / API key |
| `HF_SPACE_URL` | No | Deployed Space URL (defaults to localhost:8000) |

---

## Project structure

```
bug_triage_env/
├── __init__.py                        # exports Action, Observation, Client
├── models.py                          # BugTriageAction, BugTriageObservation
├── client.py                          # BugTriageEnv(EnvClient)
├── openenv.yaml                       # environment manifest
├── pyproject.toml
├── README.md
└── server/
    ├── bug_triage_environment.py      # Environment logic + graders
    ├── app.py                         # FastAPI app
    ├── requirements.txt
    └── Dockerfile
inference.py                           # agent loop for evaluation
```

---

## License

MIT