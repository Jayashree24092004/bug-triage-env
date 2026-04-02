import json
from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State
from models import BugTriageAction, BugTriageObservation


# ── TASK DATA ──────────────────────────────────────────────────────────────────
TASKS = {
    "easy": {
        "report": (
            "Title: Login button unresponsive on mobile\n"
            "Body: When I tap the login button on my iPhone the page "
            "just flashes but nothing happens. This started after the "
            "v2.3 update yesterday. Android works fine."
        ),
        "correct_category": "UI",
        "prompt": (
            "Classify this bug report into exactly ONE category: "
            "UI, backend, infra, or security.\n"
            'Reply with JSON: {"category": "..."}'
        ),
    },
    "medium": {
        "report": (
            "Title: API returns 500 on large file uploads\n"
            "Body: POST /api/upload fails with HTTP 500 when file >10MB. "
            "Smaller files work. Happens 100% of the time in production "
            "but not staging. Started 3 days ago, no deploys since."
        ),
        "correct_category": "backend",
        "correct_priority": "P1",
        "prompt": (
            "Classify this bug and assign a priority "
            "(P0=critical/P1=high/P2=medium/P3=low).\n"
            'Reply with JSON: {"category":"...","priority":"...","reason":"..."}'
        ),
    },
    "hard": {
        "report": (
            "Title: User data visible to other accounts\n"
            "Body: Customer #4821 reports seeing another user's order "
            "history. Reproducible. This is urgent — possible data breach. "
            "Affects EU customers per GDPR. Need immediate escalation."
        ),
        "correct_category": "security",
        "correct_priority": "P0",
        "correct_team": "security",
        "prompt": (
            "Classify, prioritise, assign to the correct team "
            "(security/backend/frontend/infra), and draft a "
            "2-sentence acknowledgement reply.\n"
            'Reply with JSON: {"category":"...","priority":"...","team":"...","reply":"..."}'
        ),
    },
}


# ── GRADERS ────────────────────────────────────────────────────────────────────
def grade_easy(response: str, task: dict) -> float:
    try:
        data = json.loads(response)
        return 1.0 if data.get("category", "").lower() == task["correct_category"].lower() else 0.0
    except Exception:
        return 0.0


def grade_medium(response: str, task: dict) -> float:
    score = 0.0
    try:
        data = json.loads(response)
        if data.get("category", "").lower() == task["correct_category"].lower():
            score += 0.4
        if data.get("priority", "").upper() == task["correct_priority"]:
            score += 0.4
        if len(data.get("reason", "")) > 10:
            score += 0.2
    except Exception:
        pass
    return round(score, 2)


def grade_hard(response: str, task: dict) -> float:
    score = 0.0
    try:
        data = json.loads(response)
        if data.get("category", "").lower() == task["correct_category"].lower():
            score += 0.3
        if data.get("priority", "").upper() == task["correct_priority"]:
            score += 0.3
        if data.get("team", "").lower() == task["correct_team"].lower():
            score += 0.2
        reply = data.get("reply", "")
        if len(reply) > 30:
            score += 0.1
        if any(w in reply.lower() for w in ["apologise", "apologi", "sorry", "acknowledge", "urgent"]):
            score += 0.1
    except Exception:
        pass
    return round(score, 2)


GRADERS = {"easy": grade_easy, "medium": grade_medium, "hard": grade_hard}


# ── ENVIRONMENT ────────────────────────────────────────────────────────────────
class BugTriageEnvironment(Environment):

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._levels = ["easy", "medium", "hard"]
        self._level_idx = 0
        self._current_level = "easy"

    def reset(self) -> BugTriageObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._level_idx = 0
        self._current_level = self._levels[0]
        task = TASKS[self._current_level]
        return BugTriageObservation(
            task_description=task["prompt"] + "\n\nBUG REPORT:\n" + task["report"],
            task_level=self._current_level,
            feedback="New episode started. Solve the easy task first.",
            reward=0.0,
            done=False,
            success=False,
        )

    def step(self, action: BugTriageAction) -> BugTriageObservation:
        self._state.step_count += 1
        level = self._current_level
        task = TASKS[level]
        reward = GRADERS[level](action.response, task)
        success = reward >= 0.8

        self._level_idx = min(self._level_idx + 1, len(self._levels) - 1)
        self._current_level = self._levels[self._level_idx]
        done = self._state.step_count >= 3

        if done:
            return BugTriageObservation(
                task_description="Episode complete.",
                task_level=level,
                feedback=f"Final step. Score: {reward}",
                reward=reward,
                done=True,
                success=success,
            )

        next_task = TASKS[self._current_level]
        return BugTriageObservation(
            task_description=next_task["prompt"] + "\n\nBUG REPORT:\n" + next_task["report"],
            task_level=self._current_level,
            feedback=f"Last score: {reward}. Next task level: {self._current_level}",
            reward=reward,
            done=False,
            success=success,
        )

    @property
    def state(self) -> State:
        return self._state