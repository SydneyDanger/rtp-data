import csv
import re

def clean_game_name(game_name):
    """Remove publisher names in parentheses and promotional text from game names."""
    # Remove anything in parentheses that looks like a publisher name
    # Pattern matches (Text) at the end of the string or anywhere in the string
    cleaned = re.sub(r'\s*\([^)]*\)\s*', ' ', game_name)
    
    # Remove promotional/review phrases (case insensitive)
    promotional_patterns = [
        r'\s+Demo\s*&\s*Review\s*',
        r'\s+Demo\s*&\s*Slot\s+Review\s*',
        r'\s+Slot\s+Review\s*&\s*Free\s+Demo\s*',
        r'\s+Review\s*&\s*Free\s+Demo\s*',
        r'\s+Review\s*,\s*Free\s+Demo\s*&[^,]*',
        r'\s+Slot\s+Review\s*&\s*Best[^,]*',
        r'\s+Slot\s+Review\s*&\s*Free\s+Online\s+Demo\s*',
        r'\s+Free\s+Demo\s*&[^,]*',
        r'\s+Game\s+ᐈ\s+RTP\s*\+\s+Game\s+info\s*',
        r'\s+Game\s+ᐈ\s+Game\s+Info\s*\+\s+Where\s+to\s+play\s*',
        r'\s+Game\s+ᐈ\s+Free\s+demo\s+game!\s*',
        r'\s+Demo\s*&\s*Slot\s+Review\s*',
        r'\s+Slot\s+Demo\s+and\s+Review\s*\|[^,]*',
        r'\s+Slot\s+Review\s*',
        r'\s+Demo\s*',
    ]
    
    for pattern in promotional_patterns:
        cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    cleaned = ' '.join(cleaned.split())
    return cleaned.strip()

def clean_csv_file(input_file, output_file):
    """Read CSV, clean game names, and write to output file."""
    rows = []
    
    # Read the CSV
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            # Clean the game name
            original_game = row['game']
            cleaned_game = clean_game_name(original_game)
            
            if original_game != cleaned_game:
                print(f"Cleaned: '{original_game}' -> '{cleaned_game}'")
            
            row['game'] = cleaned_game
            rows.append(row)
    
    # Write the cleaned data
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\nCleaned {len(rows)} rows. Output written to: {output_file}")

if __name__ == '__main__':
    input_file = 'slotcatalog_rtp_data.csv'
    output_file = 'slotcatalog_rtp_data_cleaned.csv'
    
    clean_csv_file(input_file, output_file)
