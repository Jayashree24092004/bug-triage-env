from pydantic import Field
from openenv.core.env_server.types import Action, Observation


class BugTriageAction(Action):
    response: str = Field(default="", description="JSON string with the agent's answer")


class BugTriageObservation(Observation):
    task_description: str = Field(default="", description="Bug report + instructions")
    task_level: str = Field(default="easy", description="easy | medium | hard")
    feedback: str = Field(default="", description="Score feedback from last step")
    reward: float = Field(default=0.0, description="Score 0.0–1.0")
    done: bool = Field(default=False, description="True when episode ends")
    success: bool = Field(default=False, description="True if reward >= 0.8")