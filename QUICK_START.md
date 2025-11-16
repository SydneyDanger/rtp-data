# Quick Start: SlotCatalog RTP Scraper

## Overview

You now have a complete scraping pipeline to extract RTP data from SlotCatalog and merge it with your existing CasinoListings data.

## Files Created

| File | Purpose |
|------|---------|
| `scrape_slotcatalog.py` | Main scraper - extracts game data from SlotCatalog URLs |
| `test_scraper.py` | Tests scraper on example HTML |
| `merge_rtp_data.py` | Merges CasinoListings + SlotCatalog data |
| `cloudflare_worker_proxy.js` | Optional Cloudflare Worker for proxy support |
| `SCRAPING_GUIDE.md` | Detailed documentation |

## Quick Workflow

### Step 1: Test the Scraper

```bash
pip install beautifulsoup4 requests
python test_scraper.py
```

Expected output:
```
✓ Game Name: Expected 'Alien Robots', Got 'Alien Robots'
✓ Publisher: Expected 'NetEnt', Got 'NetEnt'
✓ Min RTP: Expected '96.3', Got '96.3'
✓ Max RTP: Expected '96.6', Got '96.6'
✓ All tests passed!
```

### Step 2: (Optional) Setup Cloudflare Worker

If SlotCatalog blocks direct requests:

1. Deploy `cloudflare_worker_proxy.js` to Cloudflare Workers
2. Edit `scrape_slotcatalog.py`:
   ```python
   PROXY_URL = "https://your-worker.workers.dev/?url="
   ```

### Step 3: Run the Scraper

```bash
python scrape_slotcatalog.py
```

This will:
- Process all 3,333 URLs in `slotcatalog_urls.txt`
- Extract game name, provider, and RTP values
- Save to `slotcatalog_rtp_data.csv`
- Log errors to `slotcatalog_rtp_data_errors.txt`

**Estimated time:** 1.4 - 2.8 hours depending on delay settings

### Step 4: Merge Data Sources

```bash
python merge_rtp_data.py
```

This will:
- Combine `rtp_data.csv` (CasinoListings) + `slotcatalog_rtp_data.csv` (SlotCatalog)
- Remove duplicates (same game + publisher)
- Prefer newer/more complete data
- Save to `merged_rtp_data.csv`

### Step 5: Update Tampermonkey Script

Edit `tampermonkey-rtp-fetcher.js`:

```javascript
const CSV_URL = "https://YOUR-CLOUDFLARE-PAGES.pages.dev/merged_rtp_data.csv";
```

Upload `merged_rtp_data.csv` to your Cloudflare Pages deployment.

## Data Structure

### Input: slotcatalog_urls.txt
```
https://slotcatalog.com/en/slots/Alien-Robots
https://slotcatalog.com/en/slots/Aliens
https://slotcatalog.com/en/slots/Arabian-Nights
...
```

### Output: slotcatalog_rtp_data.csv
```csv
game,publisher,min_rtp,max_rtp,default_rtp
Alien Robots,NetEnt,96.3,96.6,96.6
Blood Suckers,NetEnt,98.0,98.0,
Arabian Nights,NetEnt,95.6,95.6,
...
```

### Final: merged_rtp_data.csv
Combines both sources, sorted by highest RTP

## Key Features

### Scraper (`scrape_slotcatalog.py`)
- Extracts game name, provider, RTP from SlotCatalog HTML
- Handles multiple RTP variants (min/max/default)
- Rate limiting (1.5s delay between requests)
- Error logging for failed URLs
- Optional Cloudflare Worker proxy support

### Merger (`merge_rtp_data.py`)
- Deduplicates based on game + publisher
- Prefers newer/more complete data
- Normalizes names for better matching
- Sorts by highest RTP

## Customization

### Adjust Scraping Speed

In `scrape_slotcatalog.py`:
```python
DELAY_BETWEEN_REQUESTS = 1.5  # Faster (risky)
DELAY_BETWEEN_REQUESTS = 3.0  # Safer
```

### Add More Data Fields

To extract additional fields (variance, max win, etc.), edit `parse_game_page()` in `scrape_slotcatalog.py`:

```python
# Example: Extract variance
variance_th = soup.find('th', class_='propLeft', string=re.compile(r'Variance', re.IGNORECASE))
if variance_th:
    variance_td = variance_th.find_next_sibling('td')
    game_data['variance'] = variance_td.get_text(strip=True)
```

## Troubleshooting

### Problem: Rate Limited / 429 Errors
**Solution:** Increase `DELAY_BETWEEN_REQUESTS` or use Cloudflare Worker proxy

### Problem: No Data Extracted
**Solution:** Run `test_scraper.py` to validate parsing logic

### Problem: Missing RTP Values
**Solution:** Check if SlotCatalog displays RTP for that game (some games don't publish it)

## Expected Results

From your 3,333 SlotCatalog URLs:
- **Success rate:** ~90-95% (some games may have no RTP data)
- **~3,000+ games** successfully scraped
- **Combined with CasinoListings:** ~5,000-6,000 unique games

This will significantly improve your Tampermonkey script's match rate!

## Next Steps

1. Run the full scrape
2. Merge with existing data
3. Upload `merged_rtp_data.csv` to Cloudflare Pages
4. Update Tampermonkey script CSV_URL
5. Test on MyPrize to see improved match rates

## Support

For issues or questions:
- Check `SCRAPING_GUIDE.md` for detailed documentation
- Review error logs: `slotcatalog_rtp_data_errors.txt`
- Inspect HTML manually if parsing fails
