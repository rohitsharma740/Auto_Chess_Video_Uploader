import os
import googleapiclient.discovery
import googleapiclient.errors
import google_auth_oauthlib.flow
import google.auth.transport.requests
import json

# Set video file and metadata
VIDEO_FILE = "chess_short.mp4"
TITLE = "Brilliant Chess Move! #Chess #Shorts"
DESCRIPTION = "Watch this incredible chess moment! Don't forget to subscribe! ♟️🔥"
TAGS = ["chess", "chess.com", "shorts", "brilliant move"]
CATEGORY_ID = "20"  # Gaming

# Authenticate and get API client
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_video():
    youtube = get_authenticated_service()
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": TITLE,
                "description": DESCRIPTION,
                "tags": TAGS,
                "categoryId": CATEGORY_ID
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=googleapiclient.http.MediaFileUpload(VIDEO_FILE)
    )

    response = request.execute()
    print(f"✅ Video uploaded successfully! YouTube Video ID: {response['id']}")

if __name__ == "__main__":
    upload_video()
