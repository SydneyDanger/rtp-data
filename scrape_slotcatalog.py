import csv
import time
import re
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

# Configuration
URLS_FILE = r"c:\Users\sydne\Desktop\rtp-data\slotcatalog_urls.txt"
OUTPUT_CSV = r"c:\Users\sydne\Desktop\rtp-data\slotcatalog_rtp_data.csv"

# If you have a Cloudflare proxy, set it here
# Example: PROXY_URL = "https://slotcatalog-lookup.sydneyoreilly.workers.dev/?url="
PROXY_URL = "https://slotcatalog-lookup.sydneyoreilly.workers.dev/?url="

# Request settings
DELAY_BETWEEN_REQUESTS = 1.5  # seconds
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def fetch_page(url: str) -> str:
    """Fetch a page with optional proxy support."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    fetch_url = f"{PROXY_URL}{url}" if PROXY_URL else url
    
    try:
        response = requests.get(fetch_url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


def parse_rtp_values(rtp_text: str, tooltip_text: str = "") -> tuple:
    """
    Parse RTP values from the main RTP text and optional tooltip.
    Returns (min_rtp, max_rtp, default_rtp)
    """
    # Remove % and convert to float
    def clean_rtp(text):
        match = re.search(r'(\d+\.?\d*)\s*%?', text)
        return float(match.group(1)) if match else None
    
    # Primary RTP value
    primary_rtp = clean_rtp(rtp_text)
    
    # Check tooltip for multiple RTP values
    # Example: "243 bet ways activated 96.6% 243 bet ways deactivated 96.3%"
    rtp_values = []
    if tooltip_text:
        # Find all percentage values in tooltip
        tooltip_matches = re.findall(r'(\d+\.?\d*)\s*%', tooltip_text)
        rtp_values = [float(v) for v in tooltip_matches]
    
    # If we have multiple RTP values from tooltip
    if len(rtp_values) > 1:
        min_rtp = min(rtp_values)
        max_rtp = max(rtp_values)
        default_rtp = primary_rtp if primary_rtp in rtp_values else max_rtp
    elif len(rtp_values) == 1:
        # Single RTP value
        min_rtp = max_rtp = rtp_values[0]
        default_rtp = None
    elif primary_rtp:
        # Only primary RTP, no tooltip info
        min_rtp = max_rtp = primary_rtp
        default_rtp = None
    else:
        # No RTP found
        return (None, None, None)
    
    return (min_rtp, max_rtp, default_rtp)


def parse_game_page(html: str, url: str) -> dict:
    """Parse a SlotCatalog game page and extract game data."""
    soup = BeautifulSoup(html, 'html.parser')
    
    game_data = {
        'game': None,
        'publisher': None,
        'min_rtp': None,
        'max_rtp': None,
        'default_rtp': None,
        'url': url
    }
    
    # Extract game name from <h1 class="mainTitle">
    title_elem = soup.find('h1', class_='mainTitle')
    if title_elem:
        # Remove "Play " prefix and " Slot" suffix if present
        game_name = title_elem.get_text(strip=True)
        game_name = re.sub(r'^Play\s+', '', game_name)
        game_name = re.sub(r'\s+Slot$', '', game_name)
        game_data['game'] = game_name
    
    # Extract provider from the attributes table
    # Look for <th class="propLeft">Provider:</th>
    provider_th = soup.find('th', class_='propLeft', string=re.compile(r'Provider:', re.IGNORECASE))
    if provider_th:
        provider_td = provider_th.find_next_sibling('td', class_='propRight')
        if provider_td:
            provider_link = provider_td.find('a')
            if provider_link:
                game_data['publisher'] = provider_link.get_text(strip=True)
    
    # Extract RTP from the attributes table
    # Look for <th class="propLeft">RTP:</th> or similar
    rtp_th = soup.find('th', class_='propLeft', string=re.compile(r'RTP', re.IGNORECASE))
    if rtp_th:
        rtp_td = rtp_th.find_next_sibling('td', class_='propRight')
        if rtp_td:
            # Get primary RTP text
            rtp_link = rtp_td.find('a')
            rtp_text = rtp_link.get_text(strip=True) if rtp_link else rtp_td.get_text(strip=True)
            
            # Get tooltip with additional RTP info (if exists)
            tooltip_span = rtp_td.find('span', class_=['spinfoPointUp', 'sarInfo'])
            tooltip_text = ""
            if tooltip_span and tooltip_span.get('title'):
                tooltip_text = tooltip_span.get('title')
            
            # Parse RTP values
            min_rtp, max_rtp, default_rtp = parse_rtp_values(rtp_text, tooltip_text)
            game_data['min_rtp'] = min_rtp
            game_data['max_rtp'] = max_rtp
            game_data['default_rtp'] = default_rtp
    
    return game_data


def scrape_all_games():
    """Main scraping function."""
    # Read URLs
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(urls)} URLs to scrape")
    
    # Prepare results
    results = []
    errors = []
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Scraping: {url}")
        
        # Fetch page
        html = fetch_page(url)
        if not html:
            errors.append(url)
            print(f"  ✗ Failed to fetch")
            continue
        
        # Parse page
        try:
            game_data = parse_game_page(html, url)
            
            if game_data['game'] and game_data['publisher']:
                results.append(game_data)
                print(f"  ✓ {game_data['game']} ({game_data['publisher']}) - RTP: {game_data['min_rtp']}")
            else:
                print(f"  ⚠ Incomplete data: {game_data}")
                errors.append(url)
        except Exception as e:
            print(f"  ✗ Parse error: {e}")
            errors.append(url)
        
        # Rate limiting
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Write results to CSV
    print(f"\n{'='*60}")
    print(f"Scraped: {len(results)} games")
    print(f"Errors: {len(errors)} URLs")
    
    if results:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['game', 'publisher', 'min_rtp', 'max_rtp', 'default_rtp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'game': result['game'],
                    'publisher': result['publisher'],
                    'min_rtp': result['min_rtp'] if result['min_rtp'] is not None else '',
                    'max_rtp': result['max_rtp'] if result['max_rtp'] is not None else '',
                    'default_rtp': result['default_rtp'] if result['default_rtp'] is not None else ''
                })
        
        print(f"✓ Wrote {len(results)} games to {OUTPUT_CSV}")
    
    if errors:
        error_file = OUTPUT_CSV.replace('.csv', '_errors.txt')
        with open(error_file, 'w', encoding='utf-8') as f:
            for url in errors:
                f.write(f"{url}\n")
        print(f"✓ Wrote {len(errors)} error URLs to {error_file}")


if __name__ == "__main__":
    print("SlotCatalog RTP Scraper")
    print("="*60)
    scrape_all_games()
