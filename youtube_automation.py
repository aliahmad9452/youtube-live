import os
import json
import requests
import base64
from datetime import datetime
from googleapiclient.discovery import build

CHANNEL_ID = "UCWHpL9Vm9toVlZ4hIMmqwCA"
API_KEY = os.getenv("YT_API_KEY")
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "aliahmad9452/youtube-live"  # Just username/repo, no .git

def update_github(playlist):
    url = f"https://api.github.com/repos/{REPO}/contents/playlist.json"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # First try to get the existing file
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    # Prepare the update
    data = {
        "message": f"Auto-update at {datetime.utcnow().isoformat()}",
        "content": base64.b64encode(json.dumps(playlist).encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    
    # Debug print (will appear in workflow logs)
    print("Attempting to update GitHub with:", json.dumps(data, indent=2)[:500] + "...")
    
    response = requests.put(url, headers=headers, json=data)
    print("GitHub API response:", response.status_code, response.text)

