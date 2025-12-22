import csv
import os
import argparse
import re

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

def main(csv_path, dir_path, output_path):
    track_map, headers = read_csv_tracks(csv_path)
    dir_tracks = read_directory_tracks(dir_path)

    csv_keys = set(track_map.keys())

    missing_from_dir = csv_keys - dir_tracks
    
    print(f"Tracks in CSV: {len(csv_keys)}")
    print(f"Printing CSV Normalized List")
    write_list_to_file("csv_keys.txt", csv_keys)
 
    print(f"Tracks in directory: {len(dir_tracks)}")
    print(f"Printing directory Normalized List")
    write_list_to_file("directory.txt", dir_tracks)

    print(f"Missing from directory: {len(missing_from_dir)}")
    print(f"Printing missing List")
    write_list_to_file("missing.txt", missing_from_dir)

    if missing_from_dir:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for key in sorted(missing_from_dir):
                writer.writerow(track_map[key])

        print(f"Wrote missing track CSV → {output_path}")
    else:
        print("No missing tracks 🎉")

    # End of part 1 (Basic matching with no artist rewrites)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare CSV tracks vs directory files")
    parser.add_argument("csv", help="Path to Spotify CSV file")
    parser.add_argument("directory", help="Directory containing music files")
    parser.add_argument(
        "-o", "--output",
        default="missing_tracks.csv",
        help="Output CSV filename (default missing_tracks.csv)"
    )
    args = parser.parse_args()

    main(args.csv, args.directory, args.output)

