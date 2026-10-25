
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

ANYTHINGLLM_BASE_URL = os.getenv(
    "ANYTHINGLLM_BASE_URL",
    "http://localhost:3001/api|brx-1EV50S2-41G4468-NZYX14X-CGNCJ2S",
).rstrip("/")

ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "W1J5F0Q-DM8M8CN-JQTMTJ3-BDW043J")
ANYTHINGLLM_WORKSPACE = os.getenv("ANYTHINGLLM_WORKSPACE", "workspace").strip()
