import os, json
from openai import OpenAI
from server.models import BugTriageAction, BugTriageEnv

# ── required env variables ─────────────────────────────────────
API_BASE_URL = os.environ["API_BASE_URL"]
MODEL_NAME   = os.environ["MODEL_NAME"]
HF_TOKEN     = os.environ["HF_TOKEN"]
SPACE_URL    = os.environ.get("HF_SPACE_URL", "http://localhost:8000")

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

def ask_llm(task_description: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a bug triage expert. Always reply with valid JSON only."
            },
            {
                "role": "user",
                "content": task_description
            },
        ],
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()


def run_episode():
    scores = []

    with BugTriageEnv(base_url=SPACE_URL).sync() as env:
        obs = env.reset()

        print(f"Episode started — first task: {obs.observation.task_level}")

        while not obs.observation.done:

            llm_answer = ask_llm(obs.observation.task_description)

            print(f"\nAgent response: {llm_answer}")

            obs = env.step(
                BugTriageAction(response=llm_answer)
            )

            print(
                f"Reward: {obs.reward} | Feedback: {obs.observation.feedback}"
            )

            scores.append(obs.reward)

    avg = round(sum(scores) / len(scores), 3) if scores else 0

    print(f"\n=== Final scores: {scores} | Average: {avg} ===")

    return scores


if __name__ == "__main__":
    run_episode()