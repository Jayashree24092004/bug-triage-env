from openenv.core.env_client import EnvClient
from server.models import BugTriageAction, BugTriageObservation


class BugTriageEnv(EnvClient):
    """
    Typed client for the Bug Triage environment.

    Usage (sync):
        with BugTriageEnv(base_url="http://localhost:8000").sync() as env:
            obs = env.reset()
            result = env.step(BugTriageAction(response='{"category": "UI"}'))

    Usage (async):
        async with BugTriageEnv(base_url="https://your-space.hf.space") as env:
            obs = await env.reset()
            result = await env.step(BugTriageAction(response='{"category": "UI"}'))
    """

    # Tell the base client which models to use for (de)serialisation
    action_class = BugTriageAction
    observation_class = BugTriageObservation