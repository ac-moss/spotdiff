import csv
import os
import spotipy
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


def create_playlist_from_csv(csv_path, playlist_name="SpotDiff Missing Tracks"):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="",
        client_secret="",
        redirect_uri="",
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
    csv_path = "missing.csv"  # <-- your file
    create_playlist_from_csv(csv_path)
