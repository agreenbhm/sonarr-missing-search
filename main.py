import os
import requests
from datetime import datetime, timedelta, timezone

# --- Configuration ---
SONARR_URL = os.environ.get("SONARR_URL", "http://sonarr:8989")
API_KEY = os.environ.get("SONARR_API_KEY", "")
DAYS_BACK = int(os.environ.get("DAYS_BACK", 7))

HEADERS = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def trigger_recent_missing_search():
    # 1. Fetch the wanted/missing list
    url_missing = f"{SONARR_URL}/api/v3/wanted/missing"
    params = {
        "page": 1,
        "pageSize": 1000, # Adjust if your missing list is massive
        "sortKey": "airDateUtc",
        "sortDirection": "descending"
    }
    
    response = requests.get(url_missing, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
    episode_ids = []

    # 2. Filter for recently aired episodes
    for record in data.get('records', []):
        air_date_str = record.get('airDateUtc')
        if not air_date_str:
            continue
            
        try:
            # Strip milliseconds/Z for consistent parsing
            air_date = datetime.strptime(air_date_str[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
            
        if air_date >= cutoff_date:
            episode_ids.append(record['id'])

    if not episode_ids:
        print("No missing episodes found within the specified timeframe.")
        return

    print(f"Found {len(episode_ids)} missing episode(s) aired in the last {DAYS_BACK} days.")

    # 3. Trigger active search for those specific IDs
    url_command = f"{SONARR_URL}/api/v3/command"
    payload = {
        "name": "EpisodeSearch",
        "episodeIds": episode_ids
    }
    
    cmd_response = requests.post(url_command, headers=HEADERS, json=payload)
    cmd_response.raise_for_status()
    print("Search command successfully dispatched to Sonarr.")

if __name__ == "__main__":
    trigger_recent_missing_search()
