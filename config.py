import os
from dotenv import load_dotenv

load_dotenv()

JELLYFIN_URL = os.getenv("JELLYFIN_URL")
JELLYFIN_API_KEY = os.getenv("JELLYFIN_API_KEY")
JELLYFIN_USER_ID = os.getenv("JELLYFIN_USER_ID")

NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

STATE_FILE = "state.json"

LIMIT = int(os.getenv("LIMIT", "20"))
