# SlotCatalog RTP Scraping Guide

This guide explains how to scrape RTP data from SlotCatalog and create a CSV database.

## Files Created

1. **scrape_slotcatalog.py** - Main scraping script
2. **test_scraper.py** - Test script to validate parsing logic
3. **cloudflare_worker_proxy.js** - Optional Cloudflare Worker for proxy support
4. **slotcatalog_urls.txt** - List of URLs to scrape (already exists)

## Quick Start

### Option 1: Direct Scraping (No Proxy)

If SlotCatalog doesn't block your requests:

```bash
# Install dependencies
pip install beautifulsoup4 requests

# Test the scraper on example HTML
python test_scraper.py

# Run the full scrape
python scrape_slotcatalog.py
```

### Option 2: With Cloudflare Worker Proxy

If you need to bypass rate limiting or CORS:

#### Step 1: Deploy Cloudflare Worker

1. Go to https://dash.cloudflare.com/
2. Navigate to Workers & Pages
3. Click "Create Application" → "Create Worker"
4. Name it (e.g., "slotcatalog-proxy")
5. Click "Deploy"
6. Click "Edit Code"
7. Copy contents of `cloudflare_worker_proxy.js` and paste it
8. Click "Save and Deploy"
9. Copy your worker URL (e.g., `https://slotcatalog-proxy.your-subdomain.workers.dev`)

#### Step 2: Configure Scraper

Edit `scrape_slotcatalog.py` and set:

```python
PROXY_URL = "https://slotcatalog-proxy.your-subdomain.workers.dev/?url="
```

#### Step 3: Run Scraper

```bash
python scrape_slotcatalog.py
```

## Configuration

In `scrape_slotcatalog.py`, you can adjust:

```python
# Time between requests (seconds)
DELAY_BETWEEN_REQUESTS = 1.5

# Increase if you get rate limited
DELAY_BETWEEN_REQUESTS = 3.0

# User agent string
USER_AGENT = "Mozilla/5.0 ..."
```

## Output Files

### slotcatalog_rtp_data.csv
Main output with columns:
- `game` - Game name
- `publisher` - Game provider/developer
- `min_rtp` - Minimum RTP percentage
- `max_rtp` - Maximum RTP percentage
- `default_rtp` - Default RTP percentage (if specified)

### slotcatalog_rtp_data_errors.txt
List of URLs that failed to scrape (if any)

## Understanding RTP Values

Some games have multiple RTP configurations:

**Example: Alien Robots**
- Min RTP: 96.3% (with 243 bet ways deactivated)
- Max RTP: 96.6% (with 243 bet ways activated)
- Default RTP: 96.6%

The scraper automatically:
1. Extracts the primary RTP from the page
2. Checks tooltips for additional RTP variants
3. Calculates min/max from all found values
4. Sets default_rtp to the primary/most common value

## Merging with Existing Data

To combine with your existing `rtp_data.csv`:

```python
import pandas as pd

# Read both CSVs
existing = pd.read_csv('rtp_data.csv')
new_data = pd.read_csv('slotcatalog_rtp_data.csv')

# Combine (remove duplicates based on game+publisher)
combined = pd.concat([existing, new_data])
combined = combined.drop_duplicates(subset=['game', 'publisher'], keep='last')

# Sort by max_rtp descending
combined = combined.sort_values('max_rtp', ascending=False)

# Save
combined.to_csv('merged_rtp_data.csv', index=False)
```

## Troubleshooting

### Issue: 403/429 Errors

**Solution:** Use the Cloudflare Worker proxy or increase `DELAY_BETWEEN_REQUESTS`

### Issue: No RTP Found

Check if SlotCatalog changed their HTML structure:
1. Save a problematic page HTML manually
2. Inspect the HTML in browser DevTools
3. Update the parsing selectors in `parse_game_page()` function

### Issue: Incomplete Data

Some games may not have all fields. The scraper handles this gracefully:
- Missing RTP → Empty in CSV
- Missing provider → Empty in CSV
- Missing game name → URL logged to errors file

## Performance

- **3,333 URLs** in your list
- **1.5 seconds** per request = ~1.4 hours total
- **3.0 seconds** per request = ~2.8 hours total (safer)

## Rate Limiting Best Practices

1. **Use realistic delays** (1.5-3 seconds)
2. **Use Cloudflare Worker** to distribute requests
3. **Scrape during off-peak hours** (less likely to be blocked)
4. **Resume capability**: Script creates error log, you can retry failed URLs

## Legal & Ethical Considerations

- Check SlotCatalog's `robots.txt` and Terms of Service
- Use data responsibly and give credit where appropriate
- Consider contacting SlotCatalog for an official data feed
- Respect rate limits and don't overload their servers

## Next Steps

After scraping:

1. **Validate data**: Check for missing values, outliers
2. **Merge with existing CSV**: Combine CasinoListings + SlotCatalog data
3. **Update Tampermonkey script**: Point to new merged CSV
4. **Schedule updates**: Re-run scraper periodically for new games
