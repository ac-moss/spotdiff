import csv
import os
import spotipy
import argparse
from dotenv import load_dotenv
from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth



def load_track_uris(csv_path):
    uris = []
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            
            uri = row[0].strip()

            # must start with spotify:track:
            if uri.startswith("spotify:track:"):
                uris.append(uri)

    return uris


def create_playlist_from_csv(csv_path, playlist_name=None):
        # If no name provided, use default + current date
    if playlist_name is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        playlist_name = f"SpotDiff Missing Tracks {date_str}"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="playlist-modify-private playlist-modify-public"
    ))

    user_id = sp.me()["id"]
    print(f"Logged in as: {user_id}")

    uris = load_track_uris(csv_path)
    print(f"Loaded {len(uris)} tracks from CSV")

    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=False,
        description="Generated from spotdiff missing tracks CSV"
    )

    playlist_id = playlist["id"]

    # Spotify only allows adding 100 at a time
    for i in range(0, len(uris), 100):
        chunk = uris[i:i+100]
        sp.playlist_add_items(playlist_id, chunk)

    print(f"Playlist created: {playlist['external_urls']['spotify']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a spotify playlist from csv following exportify.net schema")
    parser.add_argument("csv", help="Path to Spotify CSV file")
    args = parser.parse_args()
    
    load_dotenv()
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    create_playlist_from_csv(args.csv)
