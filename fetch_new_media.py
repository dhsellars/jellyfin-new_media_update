import json
import os
import requests
from config import (
    JELLYFIN_URL, JELLYFIN_API_KEY, JELLYFIN_USER_ID,
    NTFY_URL, STATE_FILE, LIMIT
)

def load_state():
    """Load previously notified item IDs."""
    if not os.path.exists(STATE_FILE):
        return {"notified_ids": []}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    """Save updated notified item IDs."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def fetch_latest():
    """Fetch latest movies and episodes from Jellyfin."""
    url = f"{JELLYFIN_URL}/Users/{JELLYFIN_USER_ID}/Items/Latest"
    params = {
        "api_key": JELLYFIN_API_KEY,
        "IncludeItemTypes": "Movie,Episode",
        "Limit": LIMIT
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def notify(title, body):
    payload = {"message": body}
    requests.post(NTFY_URL, json=payload)

def main():
    state = load_state()
    notified = set(state["notified_ids"])

    items = fetch_latest()
    new_items = [i for i in items if i["Id"] not in notified]

    if not new_items:
        return  # Nothing new this run

    for item in new_items:
        item_id = item["Id"]
        type_ = item["Type"]

        if type_ == "Episode":
            series = item.get("SeriesName", "Unknown Series")
            season = item.get("ParentIndexNumber", 0)
            episode = item.get("IndexNumber", 0)
            ep_title = item.get("Name", "")

            if ep_title:
                body = f"{series} — S{season:02}E{episode:02} — {ep_title}"
            else:
                body = f"{series} — S{season:02}E{episode:02}"

            title = f"New Episode: {series}"

        else:  # Movie
            name = item.get("Name", "Unknown Movie")
            year = item.get("ProductionYear", "")
            body = f"{name} ({year})"
            title = f"New Movie: {name}"

        notify(title, body)
        notified.add(item_id)

    # Keep only the most recent 500 IDs
    MAX_IDS = 500
    if len(notified) > MAX_IDS:
        notified = set(list(notified)[-MAX_IDS:])

    state["notified_ids"] = list(notified)
    save_state(state)

if __name__ == "__main__":
    main()
