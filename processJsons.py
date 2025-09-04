import json
import csv
from pathlib import Path
from datetime import datetime

def process_spotify_history_combined_and_split(folder_path, output_folder, combined_csv):
    folder = Path(folder_path)
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    jsons = list(folder.glob('Streaming_History_Audio_*.json'))
    records = []

    for file_path in jsons:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for entry in data:
                timestamp = entry.get('ts')
                if not timestamp:
                    continue  # sskips if there is no timestamp (error on a few lines)
                ms_played = entry.get('ms_played')
                
                # Filter out tracks longer than 1 hour (3,600,000 ms)
                if ms_played and ms_played > 3600000:
                    continue
                
                record = {
                    'timestamp': timestamp,
                    'platform': entry.get('platform'),
                    'ms_played': ms_played,
                    'track_name': entry.get('master_metadata_track_name'),
                    'artist': entry.get('master_metadata_album_artist_name'),
                    'album': entry.get('master_metadata_album_album_name'),
                    'spotify_uri': entry.get('spotify_track_uri'),
                    'skipped': entry.get('skipped'),
                    'shuffle': entry.get('shuffle'),
                    'offline': entry.get('offline'),
                    'incognito_mode': entry.get('incognito_mode'),
                    'source_file': file_path.name
                }
                records.append(record)

    # Sort by timestamp
    records.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')))

    fieldnames = ['timestamp', 'platform', 'ms_played', 'track_name', 'artist', 'album', 'spotify_uri', 'skipped', 'shuffle', 'offline', 'incognito_mode', 'source_file']

    #combined csv of all years
    with open(combined_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)
    print(f"{len(records)} rows to {combined_csv}")

    #yearly csvs
    records_by_year = {}
    for record in records:
        year = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')).year
        if year not in records_by_year:
            records_by_year[year] = []
        records_by_year[year].append(record)


    for year, records in records_by_year.items():
        output_path = output_dir / f'spotify_history_{year}.csv'
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record)
        print(f"{len(records)} rows to {year} in {output_path}")

#run the process function
process_spotify_history_combined_and_split('./data','./outputByYear','spotify_history_all_years.csv')
