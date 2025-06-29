import os
import json
import requests
import base64  # Added for proper base64 encoding
from datetime import datetime
from googleapiclient.discovery import build

# Configuration
CHANNEL_ID = "UCWHpL9Vm9toVlZ4hIMmqwCA"  # Your channel ID
API_KEY = os.getenv("YT_API_KEY")
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "aliahmad9452/youtube-live"  # Format: "username/repo" (NOT full git URL)

def fetch_videos():
    """Fetch all video IDs from your channel"""
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
    """Generate playlist JSON structure"""
    return {
        "last_updated": datetime.utcnow().isoformat(),
        "videos": video_ids,
        "total_duration": len(video_ids) * 600,  # 10 minutes per video
        "description": "Auto-generated 24/7 YouTube playlist"
    }

def update_github(playlist):
    """Update playlist.json in GitHub repo"""
    url = f"https://api.github.com/repos/{REPO}/contents/playlist.json"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get current file SHA if it exists
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    # Prepare update data with PROPER base64 encoding
    data = {
        "message": f"Auto-update at {datetime.utcnow().isoformat()}",
        "content": base64.b64encode(json.dumps(playlist).encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    
    # Push update
    response = requests.put(url, headers=headers, json=data)
    if response.status_code not in [200, 201]:
        print(f"Failed to update GitHub: {response.text}")

if __name__ == "__main__":
    try:
        videos = fetch_videos()
        if not videos:
            raise ValueError("No videos found in channel!")
            
        playlist = generate_playlist(videos)
        update_github(playlist)
        print("Successfully updated playlist!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
