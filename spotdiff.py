import csv
import os
import argparse
import re
import difflib
from mutagen.easyid3 import EasyID3

OUTPUT_DIR="logs"


def normalize(s):
    if s is None:
        return ""
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return s.strip()

def read_csv_tracks(csv_path):
    track_map = {}

    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        for row in reader:
            track = normalize(row.get("Track Name"))

            artists_raw = row.get("Artist Name(s)", "")
            main_artist = artists_raw.split(";")[0].strip()
            main_artist = normalize(main_artist)

            key = f"{track} {main_artist}".strip()

            if key:
                track_map[key] = row

    return track_map, headers

def normalize_track_only_map(csv_path):
    track_only_map = {}

    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            track = normalize(row.get("Track Name"))

            if track and track not in track_only_map:
                track_only_map[track] = row

    return track_only_map


# EXPERIMENTAL - DO NOT USE YET
def read_directory_tracks_with_artist2(dir_path):
    
    files_with_artist = set()

    for root, _, filenames in os.walk(dir_path):
        for name in filenames:
            base, _ = os.path.splitext(name)
            norm = normalize(base)
            artist = ""

            try:
                tags = EasyID3(name)
                artist= tags.get("artist", ["Unknown Artist"])[0]
            except Exception:
                artist = "Unknown Artist"

            files_with_artist.add(f"{norm} {artist}")

    return files_with_artist
         

def read_directory_tracks_with_artist(dir_path, track_only_map, cutoff=0.7):
    """
    dir_path: folder of your music files
    track_only_map: dict { normalized_track : csv_row }
                    (same one you already built earlier)
    cutoff: fuzzy match threshold
    """
    files_with_artist = set()
    track_only_keys = list(track_only_map.keys())

    for root, _, filenames in os.walk(dir_path):
        for name in filenames:
            base, _ = os.path.splitext(name)
            norm = normalize(base)

            # exact match first
            if norm in track_only_map:
                row = track_only_map[norm]
            else:
                # fuzzy fallback
                best = difflib.get_close_matches(norm, track_only_keys, n=1, cutoff=cutoff)
                if not best:
                    continue
                row = track_only_map[best[0]]

            track = normalize(row["Track Name"])
            main_artist = normalize(row["Artist Name(s)"].split(";")[0])

            files_with_artist.add(f"{track} {main_artist}")

    return files_with_artist

def read_directory_tracks(dir_path):
    files = set()
    
    for root, _, filenames in os.walk(dir_path):
        for name in filenames:
            base, _ = os.path.splitext(name)
            files.add(normalize(base))
    
    return files

def write_list_to_file(filename, items):
    with open(filename, "w", encoding="utf-8") as f:
        for item in items:
            f.write(f"{item}\n")

def write_csv(data, map, headers, output_path):
    if data:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for key in sorted(data):
                writer.writerow(map[key])

        print(f"Wrote missing track CSV → {output_path}")
    else:
        print("No missing tracks 🎉")


def main(csv_path, dir_path, output_path):
    track_map, headers = read_csv_tracks(csv_path)
    track_only_map = normalize_track_only_map(csv_path)

    # directory → enriched with artist names
    #dir_tracks = read_directory_tracks_with_artist2(dir_path)
    dir_tracks = read_directory_tracks_with_artist(dir_path, track_only_map)

    csv_keys = set(track_map.keys())
    missing_from_dir = csv_keys - dir_tracks
    
    print(f"Tracks in CSV: {len(csv_keys)}")
    print(f"Tracks in directory (artist-aware): {len(dir_tracks)}")
    print(f'Tracks missing: {len(missing_from_dir)}')


    if args.debug:
        print("\n[DEBUG] Debug Mode Enabled")
        print("[DEBUG] Writing diagnostic files...")

        print("  • csv.txt       → All normalized CSV track keys "
            "(track + main artist)")
        print("  • directory.txt → All normalized directory track keys "
            "(after artist fill + fuzzy match)")
        print("  • missing.txt   → Tracks in CSV that are NOT found "
            "in the directory")

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        write_list_to_file(os.path.join(OUTPUT_DIR, "csv.txt"), csv_keys)
        write_list_to_file(os.path.join(OUTPUT_DIR, "directory.txt"), dir_tracks)
        write_list_to_file(os.path.join(OUTPUT_DIR,"missing.txt"), missing_from_dir)
        write_list_to_file(os.path.join(OUTPUT_DIR,"track_only_map.txt"), track_only_map)

        print("[DEBUG] Done writing debug files.\n")

    write_csv(missing_from_dir, track_map, headers, output_path)

    input("Press Enter to exit...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare CSV tracks vs directory files")
    parser.add_argument("csv", help="Path to Spotify CSV file")
    parser.add_argument("directory", help="Directory containing music files")
    parser.add_argument(
        "-o", "--output",
        default="missing_tracks.csv",
        help="Output CSV filename (default missing_tracks.csv)"
    )
    parser.add_argument(
        "--debug", "-v",
        action="store_true",
        help="Enable verbose debug output"
    )
    args = parser.parse_args()

    main(args.csv, args.directory, args.output)

