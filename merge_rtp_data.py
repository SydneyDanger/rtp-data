"""
Merge RTP data from multiple sources into a single CSV
Handles duplicates and normalizes data
"""
import csv
from collections import defaultdict

# Input files
CASINOLISTINGS_CSV = r"c:\Users\sydne\Desktop\rtp-data\rtp_data.csv"
SLOTCATALOG_CSV = r"c:\Users\sydne\Desktop\rtp-data\slotcatalog_rtp_data.csv"
OUTPUT_CSV = r"c:\Users\sydne\Desktop\rtp-data\merged_rtp_data.csv"


def normalize_name(text):
    """Normalize game/publisher names for comparison."""
    if not text:
        return ""
    return text.lower().strip().replace("'", "'")


def read_csv_data(filepath):
    """Read CSV and return list of game dicts."""
    games = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                games.append({
                    'game': row.get('game', '').strip(),
                    'publisher': row.get('publisher', '').strip(),
                    'min_rtp': float(row['min_rtp']) if row.get('min_rtp') else None,
                    'max_rtp': float(row['max_rtp']) if row.get('max_rtp') else None,
                    'default_rtp': float(row['default_rtp']) if row.get('default_rtp') else None,
                })
        print(f"✓ Read {len(games)} games from {filepath}")
    except FileNotFoundError:
        print(f"⚠ File not found: {filepath}")
    except Exception as e:
        print(f"✗ Error reading {filepath}: {e}")
    
    return games


def merge_game_data(game1, game2):
    """
    Merge two game records, preferring non-null values.
    If both have values, prefer game2 (newer/SlotCatalog data).
    """
    merged = {
        'game': game2['game'] or game1['game'],
        'publisher': game2['publisher'] or game1['publisher'],
        'min_rtp': game2['min_rtp'] if game2['min_rtp'] is not None else game1['min_rtp'],
        'max_rtp': game2['max_rtp'] if game2['max_rtp'] is not None else game1['max_rtp'],
        'default_rtp': game2['default_rtp'] if game2['default_rtp'] is not None else game1['default_rtp'],
    }
    return merged


def merge_datasets():
    """Main merge logic."""
    print("="*60)
    print("Merging RTP Data from Multiple Sources")
    print("="*60)
    
    # Read both datasets
    casinolistings_games = read_csv_data(CASINOLISTINGS_CSV)
    slotcatalog_games = read_csv_data(SLOTCATALOG_CSV)
    
    # Create a dictionary keyed by (normalized_game_name, normalized_publisher)
    merged_dict = {}
    
    # Add CasinoListings data
    for game in casinolistings_games:
        key = (normalize_name(game['game']), normalize_name(game['publisher']))
        merged_dict[key] = game
    
    # Merge SlotCatalog data
    duplicates = 0
    new_games = 0
    
    for game in slotcatalog_games:
        key = (normalize_name(game['game']), normalize_name(game['publisher']))
        
        if key in merged_dict:
            # Duplicate found - merge the data
            merged_dict[key] = merge_game_data(merged_dict[key], game)
            duplicates += 1
        else:
            # New game
            merged_dict[key] = game
            new_games += 1
    
    # Convert back to list and sort by max_rtp (descending)
    merged_list = list(merged_dict.values())
    merged_list.sort(key=lambda x: (x['max_rtp'] or 0), reverse=True)
    
    # Write to output CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['game', 'publisher', 'min_rtp', 'max_rtp', 'default_rtp']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for game in merged_list:
            writer.writerow({
                'game': game['game'],
                'publisher': game['publisher'],
                'min_rtp': game['min_rtp'] if game['min_rtp'] is not None else '',
                'max_rtp': game['max_rtp'] if game['max_rtp'] is not None else '',
                'default_rtp': game['default_rtp'] if game['default_rtp'] is not None else '',
            })
    
    # Summary
    print("="*60)
    print("Merge Summary:")
    print(f"  CasinoListings games: {len(casinolistings_games)}")
    print(f"  SlotCatalog games: {len(slotcatalog_games)}")
    print(f"  Duplicates merged: {duplicates}")
    print(f"  New games added: {new_games}")
    print(f"  Total unique games: {len(merged_list)}")
    print("="*60)
    print(f"✓ Wrote merged data to: {OUTPUT_CSV}")
    
    # Show top 10 highest RTP games
    print("\nTop 10 Highest RTP Games:")
    for i, game in enumerate(merged_list[:10], 1):
        rtp = game['max_rtp'] or game['min_rtp'] or 'N/A'
        print(f"  {i}. {game['game']} ({game['publisher']}) - {rtp}%")


if __name__ == "__main__":
    merge_datasets()
