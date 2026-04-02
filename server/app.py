import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from fastapi.middleware.cors import CORSMiddleware
from openenv.core.env_server import create_app
from bug_triage_environment import BugTriageEnvironment
from models import BugTriageAction, BugTriageObservation

app = create_app(
    BugTriageEnvironment,
    BugTriageAction,
    BugTriageObservation,
    env_name="bug-triage-env",
)

# Allow the frontend HTML file to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)