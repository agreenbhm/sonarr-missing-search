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

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def trigger_recent_missing_search():
    now_ts = get_timestamp()
    
    # 1. Fetch the wanted/missing list
    url_missing = f"{SONARR_URL}/api/v3/wanted/missing"
    params = {
        "page": 1,
        "pageSize": 1000,
        "sortKey": "airDateUtc",
        "sortDirection": "descending"
    }
    
    try:
        response = requests.get(url_missing, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[{now_ts}] Error connecting to Sonarr: {e}")
        return

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
    episode_ids = []

    # 2. Filter for recently aired episodes
    for record in data.get('records', []):
        air_date_str = record.get('airDateUtc')
        if not air_date_str: continue
            
        try:
            air_date = datetime.strptime(air_date_str[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError: continue
            
        if air_date >= cutoff_date:
            episode_ids.append(record['id'])

    # Log the search window and findings
    print(f"[{now_ts}] Check complete. Window: last {DAYS_BACK} days. Found: {len(episode_ids)} missing.")

    if not episode_ids:
        return

    # 3. Trigger active search
    url_command = f"{SONARR_URL}/api/v3/command"
    payload = {"name": "EpisodeSearch", "episodeIds": episode_ids}
    
    try:
        requests.post(url_command, headers=HEADERS, json=payload).raise_for_status()
        print(f"[{now_ts}] Search command dispatched for {len(episode_ids)} episodes.")
    except Exception as e:
        print(f"[{now_ts}] Failed to dispatch search: {e}")

if __name__ == "__main__":
    trigger_recent_missing_search()
