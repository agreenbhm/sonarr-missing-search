# sonarr-missing-search

A Docker container running simple script that triggers every 6 hours to tell Sonarr to search your indexers for any missing episodes.  This is useful if you use public trackers and/or ones that don't provide reliable RSS feeds to tell your setup when it should download new episodes.

## Usage ##
You can run the main.py script as a one-off by installing dependencies and setting the environment variables SONARR_URL and SONARR_API_KEY.
1. pip install -r requirements.txt
2. SONARR_URL=<sonarr_host_name> SONARR_API_KEY<sonarr_api_key> python3 main.py

If you want it to run every 6 hours via Docker just run it with Compose which will first build the image and then run it.
1. docker compose up -d

If you are going to use this with Portainer or something similar you need to build it yourself first (Portainer can't fully handle adding/copying files into the container during build.  Just run the Dockerfile, push the image to your system, and then deploy it with the Compose file (removing the "Build" section.
1. docker build -t agreenbhm/sonarr-missing-search:latest .
