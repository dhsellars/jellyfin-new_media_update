import json
import os
import requests
from config import (
    JELLYFIN_URL, JELLYFIN_API_KEY, JELLYFIN_USER_ID,
    NTFY_URL, STATE_FILE, LIMIT
)

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"notified_ids": []}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def fetch_latest():
    url = f"{JELLYFIN_URL}/Users/{JELLYFIN_USER_ID}/Items/Latest"
    params = {
        "api_key": JELLYFIN_API_KEY,
        "IncludeItemTypes": "Movie,Episode",
        "Limit": LIMIT
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()
    
def notify(title, body, image_url=None):
    files = None

    if image_url:
        img = requests.get(image_url, timeout=10)
        if img.status_code == 200:
            files = {"attachment": ("poster.jpg", img.content)}

    requests.post(NTFY_URL, data=body.encode("utf-8"), files=files)

def main():
    state = load_state()
    notified = set(state["notified_ids"])

    items = fetch_latest()
    new_items = [i for i in items if i["Id"] not in notified]

    if not new_items:
        return

    for item in new_items:
        item_id = item["Id"]
        name = item["Name"]
        year = item.get("ProductionYear", "")
        type_ = item["Type"]

        if type_ == "Episode":
            series = item.get("SeriesName", "")
            season = item.get("ParentIndexNumber", 0)
            episode = item.get("IndexNumber", 0)
            title = f"{series} S{season:02}E{episode:02}"
        else:
            title = f"{name} ({year})"

        body = f"New {type_}: {title}"

        poster_url = f"{JELLYFIN_URL}/Items/{item_id}/Images/Primary?api_key={JELLYFIN_API_KEY}"

        notify(title, body, poster_url)

        notified.add(item_id)

    state["notified_ids"] = list(notified)
    save_state(state)

if __name__ == "__main__":
    main()
