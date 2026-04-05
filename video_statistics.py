import json
import os
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv

# --- Configuration & Setup ---
load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "freecodecamp"
# Maximum results per YouTube API request (max allowed by Google is 50)
MAX_RESULTS_PER_PAGE = 50 

def get_playlist_id(channel_handle):
    """
    Fetches the 'uploads' playlist ID for a given YouTube channel handle.
    The 'uploads' playlist contains all public videos from that channel.
    """
    try:
        url = "https://youtube.googleapis.com/youtube/v3/channels"
        params = {
            "part": "contentDetails",
            "forHandle": channel_handle,
            "key": API_KEY
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("items"):
            return None

        # ContentDetails contains the relatedPlaylists, including the 'uploads' ID
        return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    except requests.exceptions.RequestException as ex:
        print(f"Error fetching playlist ID: {ex}")
        raise ex

def get_channel_name(channel_handle):
    """Retrieves the display name of the channel using the handle."""
    try:
        url = "https://youtube.googleapis.com/youtube/v3/channels"
        params = {
            "part": "snippet",
            "forHandle": channel_handle,
            "key": API_KEY
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("items"):
            return "Channel not found"

        return data["items"][0]["snippet"]["title"]
        
    except requests.exceptions.RequestException as ex:
        print(f"Error fetching channel name: {ex}")
        return None

def get_video_ids(playlist_id, limit=20):
    """
    Iterates through playlist items to collect video IDs up to the specified limit.
    Handles pagination using 'nextPageToken'.
    """
    video_ids = []
    page_token = None

    try:
        while len(video_ids) < limit:
            url = "https://youtube.googleapis.com/youtube/v3/playlistItems"
            params = {
                "part": "contentDetails",
                "maxResults": min(limit, MAX_RESULTS_PER_PAGE),
                "playlistId": playlist_id,
                "key": API_KEY,
                "pageToken": page_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                video_ids.append(item["contentDetails"]["videoId"])
                if len(video_ids) >= limit:
                    break

            page_token = data.get("nextPageToken")
            if not page_token:
                break
        
        return video_ids

    except requests.exceptions.RequestException as e:
        print(f"Error fetching video IDs: {e}")
        raise e

def extract_video_data(video_ids):
    """
    Fetches detailed metadata (views, likes, duration) for a list of video IDs.
    Uses batch processing to minimize API calls.
    """
    extracted_data = []
    batch_size = 50 # API allows up to 50 IDs per request

    # Helper to split list into chunks
    def chunk_list(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i : i + size]

    try:
        for batch in chunk_list(video_ids, batch_size):
            ids_query = ",".join(batch)
            url = "https://youtube.googleapis.com/youtube/v3/videos"
            params = {
                "part": "contentDetails,snippet,statistics",
                "id": ids_query,
                "key": API_KEY
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                extracted_data.append({
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                    "duration": item["contentDetails"]["duration"],
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "like_count": int(item["statistics"].get("likeCount", 0)),
                    "comment_count": int(item["statistics"].get("commentCount", 0)),
                })

        return extracted_data

    except requests.exceptions.RequestException as e:
        print(f"Error extracting video data: {e}")
        raise e

def save_to_json(data):
    """Saves the extracted data to a timestamped JSON file inside the /data directory."""
    # Ensure the data directory exists
    output_dir = Path("./data")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"youtube_data_{date.today()}.json"
    file_path = output_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"\n[SUCCESS] Data saved to: {file_path}")

# --- Main Execution ---
if __name__ == "__main__":
    print("="*60)
    print(f"INITIALIZING YOUTUBE SCRAPER FOR: @{CHANNEL_HANDLE}")
    print("="*60)

    name = get_channel_name(CHANNEL_HANDLE)
    p_id = get_playlist_id(CHANNEL_HANDLE)

    if not p_id:
        print("[ERROR] Could not find channel or playlist. Check your API key and Handle.")
    else:
        print(f"{'Channel Name:':<15} {name}")
        print(f"{'Uploads ID:':<15} {p_id}")

        # Ask the user for the number of videos
        user_input = input("Enter the number of videos to fetch (default is 10): ").strip()

        # Convert to integer, defaulting to 10 if input is empty or invalid
        try:
            target_limit = int(user_input) if user_input else 10
        except ValueError:
            print("[INFO] Invalid input detected. Defaulting to 10 videos.")
            target_limit = 10

        # Fetch the videos using the user's limit
        v_ids = get_video_ids(p_id, limit=target_limit)

        if v_ids:
            print(f"\n{'No.':<4} | {'Video ID':<15} | {'URL'}")
            print("-" * 60)
            for idx, v_id in enumerate(v_ids, 1):
                print(f"{idx:<4} | {v_id:<15} | https://youtu.be/{v_id}")
            
            print("-" * 60)

            # Dynamic pluralization for the status message
            keyword = "video" if len(v_ids) == 1 else "videos"
            print(f"Fetching metadata for {len(v_ids)} {keyword}...")
            
            final_data = extract_video_data(v_ids)
            save_to_json(final_data)
        else:
            print("No videos found in this channel.")