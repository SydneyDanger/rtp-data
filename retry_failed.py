"""
Retry failed URLs from the error log
Appends successful results to the existing CSV
"""
import csv
import time
from scrape_slotcatalog import fetch_page, parse_game_page, DELAY_BETWEEN_REQUESTS

ERROR_FILE = r"c:\Users\sydne\Desktop\rtp-data\slotcatalog_rtp_data_errors.txt"
OUTPUT_CSV = r"c:\Users\sydne\Desktop\rtp-data\slotcatalog_rtp_data.csv"
NEW_ERRORS_FILE = r"c:\Users\sydne\Desktop\rtp-data\slotcatalog_rtp_data_errors_retry.txt"


def retry_failed_urls():
    """Retry scraping failed URLs."""
    # Read error file
    try:
        with open(ERROR_FILE, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"No error file found: {ERROR_FILE}")
        return
    
    if not urls:
        print("No failed URLs to retry")
        return
    
    print(f"Found {len(urls)} failed URLs to retry")
    print("="*60)
    
    # Prepare results
    successes = []
    still_failed = []
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Retrying: {url}")
        
        # Fetch page
        html = fetch_page(url)
        if not html:
            still_failed.append(url)
            print(f"  ✗ Still failed to fetch")
            time.sleep(DELAY_BETWEEN_REQUESTS)
            continue
        
        # Parse page
        try:
            game_data = parse_game_page(html, url)
            
            if game_data['game'] and game_data['publisher']:
                successes.append(game_data)
                print(f"  ✓ {game_data['game']} ({game_data['publisher']}) - RTP: {game_data['min_rtp']}")
            else:
                print(f"  ⚠ Incomplete data")
                still_failed.append(url)
        except Exception as e:
            print(f"  ✗ Parse error: {e}")
            still_failed.append(url)
        
        # Rate limiting
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Append successful results to existing CSV
    if successes:
        with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['game', 'publisher', 'min_rtp', 'max_rtp', 'default_rtp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            for result in successes:
                writer.writerow({
                    'game': result['game'],
                    'publisher': result['publisher'],
                    'min_rtp': result['min_rtp'] if result['min_rtp'] is not None else '',
                    'max_rtp': result['max_rtp'] if result['max_rtp'] is not None else '',
                    'default_rtp': result['default_rtp'] if result['default_rtp'] is not None else ''
                })
    
    # Write new error file
    if still_failed:
        with open(NEW_ERRORS_FILE, 'w', encoding='utf-8') as f:
            for url in still_failed:
                f.write(f"{url}\n")
    
    # Summary
    print("="*60)
    print(f"Retry Summary:")
    print(f"  Original failures: {len(urls)}")
    print(f"  Now successful: {len(successes)}")
    print(f"  Still failing: {len(still_failed)}")
    print("="*60)
    
    if successes:
        print(f"✓ Appended {len(successes)} games to {OUTPUT_CSV}")
    
    if still_failed:
        print(f"✓ Wrote {len(still_failed)} still-failing URLs to {NEW_ERRORS_FILE}")
    else:
        print(f"✓ All URLs scraped successfully!")


if __name__ == "__main__":
    print("SlotCatalog RTP Scraper - Retry Failed URLs")
    print("="*60)
    retry_failed_urls()
