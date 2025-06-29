import os
import json
import requests
from datetime import datetime
from googleapiclient.discovery import build

CHANNEL_ID = "UCWHpL9Vm9toVlZ4hIMmqwCA"  # Replace with your YouTube channel ID
API_KEY = os.getenv("YT_API_KEY")
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "https://github.com/aliahmad9452/youtube-live.git"  # e.g., "TechGuy/youtube-24x7"

def fetch_videos():
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.search().list(
        channelId=CHANNEL_ID,
        type="video",
        order="date",
        part="id",
        maxResults=50
    )
    response = request.execute()
    return [item["id"]["videoId"] for item in response["items"]]

def generate_playlist(video_ids):
    return {
        "last_updated": datetime.utcnow().isoformat(),
        "videos": video_ids,
        "total_duration": len(video_ids) * 600  # 10 minutes per video
    }

def update_github(playlist):
    url = f"https://api.github.com/repos/{REPO}/contents/playlist.json"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get existing file (if any)
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    # Update file
    data = {
        "message": f"Auto-update at {datetime.utcnow().isoformat()}",
        "content": json.dumps(playlist).encode("base64").decode("utf-8"),
        "sha": sha
    }
    requests.put(url, headers=headers, json=data)

if __name__ == "__main__":
    videos = fetch_videos()
    playlist = generate_playlist(videos)
    update_github(playlist)