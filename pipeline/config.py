import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY", "")
HEYGEN_AVATAR_ID = os.getenv("HEYGEN_AVATAR_ID", "c6a50177bc544a6bb3c153906d771d01")
HEYGEN_VOICE_ID = os.getenv("HEYGEN_VOICE_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")

# If GEMINI_API_KEY is provided, configure OpenAI SDK compatibility endpoint
if GEMINI_API_KEY and not OPENAI_API_KEY:
    OPENAI_API_KEY = GEMINI_API_KEY

if GEMINI_API_KEY and not OPENAI_BASE_URL:
    OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
SYNTHESIA_API_KEY = os.getenv("SYNTHESIA_API_KEY", "")

HEYGEN_BASE_URL = "https://api.heygen.com"
SYNTHESIA_BASE_URL = "https://api.synthesia.io/v2"

# CLI overrides for avatar-id and job-id
def _get_cli_arg(flag: str) -> str | None:
    if flag in sys.argv:
        idx = sys.argv.index(flag)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return None

_avatar_override = _get_cli_arg("--avatar-id")
if _avatar_override:
    HEYGEN_AVATAR_ID = _avatar_override

_job_id = _get_cli_arg("--job-id")
_resume_id = _get_cli_arg("--resume")
RESUME_JOB_ID = _resume_id  # Set when running Phase 2 via --resume
JOB_ID = _job_id or _resume_id

# Output directory: use job-specific subdir if job-id provided
if JOB_ID:
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", JOB_ID)
else:
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# When True, trims script to first sentence before sending to HeyGen (saves credits)
HEYGEN_TEST_MODE = os.getenv("HEYGEN_TEST_MODE", "false").lower() in ("true", "1", "yes")
