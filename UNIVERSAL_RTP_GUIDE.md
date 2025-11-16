# Universal RTP Finder - Tampermonkey Script Guide

## Overview

This script automatically detects slot games on any casino website and displays RTP information from your CSV database.

## Features

### Multi-Strategy Detection
1. **URL Pattern** - Detects game URLs like `/play/game-name`
2. **DOM Elements** - Finds game name in page headers and elements
3. **Page Title** - Extracts game name from `<title>` tag
4. **Iframe Sources** - Detects provider from game iframe URLs

### Smart Matching
- Exact name + provider match
- Exact name, any provider
- Fuzzy name match (handles variations)
- Normalizes names (case, punctuation, special chars)

### Visual Widget
- Non-intrusive overlay (customizable position)
- Color-coded RTP (green = high, yellow = medium, orange = low)
- Shows RTP range if multiple values exist
- Auto-hides after 5 seconds (optional)
- Click to collapse/expand

## Installation

1. Install Tampermonkey browser extension
2. Create new script
3. Copy contents of `tampermonkey-universal-rtp.js`
4. Save and enable

## Configuration

### CSV URL

```javascript
const CSV_URL = "https://6a124d6b.rtp-data.pages.dev/rtp_data.csv";
```

Change this to your merged CSV location after scraping SlotCatalog.

### Widget Position

```javascript
const WIDGET_POSITION = 'top-right';
```

Options: `'top-right'`, `'top-left'`, `'bottom-right'`, `'bottom-left'`

### Auto-Hide

```javascript
const AUTO_HIDE_DELAY = 5000; // milliseconds
```

Set to `0` to disable auto-hide.

### Site-Specific Rules

Add custom detection rules for specific casino sites:

```javascript
const SITE_RULES = {
    'myprize.us': {
        enabled: true,
        urlPattern: /\/play\//,
        selectors: {
            gameName: 'h1, .game-title',
            provider: '.provider-name',
        }
    },
    'casino.com': {
        enabled: true,
        urlPattern: /\/games\//,
        selectors: {
            gameName: '.game-header h1',
            provider: '.game-info .developer',
        }
    },
    // ... add more sites
};
```

## How to Add a New Site

### Step 1: Identify URL Pattern

Visit a game on the site and check the URL:
```
https://example-casino.com/play/starburst
```

Create a regex pattern:
```javascript
urlPattern: /\/play\//
```

### Step 2: Find DOM Selectors

Open browser DevTools (F12) and inspect the page:

1. **Find game name element:**
   - Right-click the game name → Inspect
   - Note the selector (e.g., `h1.game-title`)

2. **Find provider element:**
   - Right-click the provider name → Inspect
   - Note the selector (e.g., `.developer-info`)

### Step 3: Add Rule

```javascript
'example-casino.com': {
    enabled: true,
    urlPattern: /\/play\//,
    selectors: {
        gameName: 'h1.game-title, .game-name',
        provider: '.developer-info, .provider',
    }
}
```

**Tip:** Use multiple selectors (comma-separated) as fallbacks.

## Detection Priority

The script tries detection methods in this order:

1. **DOM Selectors** (site-specific rules)
2. **Page Title** (common patterns like "Play Game Name | Casino")
3. **URL Path** (extracts from `/play/game-name`)
4. **Iframe Sources** (provider domains in game iframe)

## Troubleshooting

### Issue: Widget Not Appearing

**Check Console:**
```javascript
// Open DevTools → Console
// Look for [RTP Finder] messages
```

**Common causes:**
1. URL pattern doesn't match
2. Selectors are wrong
3. CSV failed to load
4. Page is not a game page

**Solution:**
```javascript
// Temporarily disable URL pattern check:
urlPattern: null, // Will try detection on all pages
```

### Issue: Wrong Game Detected

**Check detection source:**
- Widget shows source (DOM, Title, URL, Iframe)
- Add console logging to debug

**Solution:**
Add more specific selectors or adjust `cleanGameName()` function.

### Issue: No RTP Match Found

**Causes:**
1. Game name format differs from CSV
2. Game not in CSV database
3. Provider mismatch

**Debug:**
```javascript
// Add logging in matchGame():
console.log('Searching for:', gNorm, pNorm);
console.log('CSV has:', CSV_DATA.map(r => normalize(r.game)).slice(0, 10));
```

**Solution:**
- Scrape SlotCatalog for more games
- Adjust normalization logic
- Add fuzzy matching variations

### Issue: Widget Blocks Content

**Solutions:**
1. Change position: `WIDGET_POSITION = 'bottom-right'`
2. Reduce auto-hide delay: `AUTO_HIDE_DELAY = 2000`
3. Make widget draggable (add drag functionality)

## Advanced Customization

### Add More Detection Methods

```javascript
function detectFromMetaTags() {
    const gameNameMeta = document.querySelector('meta[property="og:title"]');
    const providerMeta = document.querySelector('meta[name="developer"]');
    
    if (gameNameMeta) {
        return {
            name: cleanGameName(gameNameMeta.content),
            provider: providerMeta ? providerMeta.content : 'Unknown',
            source: 'Meta'
        };
    }
    return null;
}

// Add to detectGame():
const gameInfo = 
    detectFromDOM(rules.selectors) ||
    detectFromMetaTags() ||  // NEW
    detectFromTitle() ||
    detectFromURL() ||
    detectFromIframe();
```

### Add Keyboard Shortcut

```javascript
document.addEventListener('keydown', (e) => {
    // Press 'R' to toggle widget
    if (e.key === 'r' && !e.ctrlKey && !e.altKey) {
        toggleWidget();
    }
});
```

### Export RTP History

```javascript
const history = [];

function logGameView(gameInfo, rtpMatch) {
    history.push({
        timestamp: new Date().toISOString(),
        game: gameInfo.name,
        provider: gameInfo.provider,
        rtp: rtpMatch ? rtpMatch.max_rtp : null,
        url: window.location.href
    });
    
    // Store in localStorage
    localStorage.setItem('rtp_history', JSON.stringify(history));
}
```

### Show Multiple Matches

```javascript
function searchRTP(gameInfo) {
    const matches = matchAllGames(gameInfo.name, gameInfo.provider);
    
    if (matches.length > 1) {
        showWidgetWithOptions(gameInfo, matches);
    } else if (matches.length === 1) {
        showWidget(gameInfo, matches[0]);
    } else {
        showWidget(gameInfo, null);
    }
}
```

## Performance Tips

1. **Disable on non-game pages:**
   - Add explicit URL whitelist
   - Only run on specific domains

2. **Lazy load CSV:**
   - Only load when game detected
   - Cache CSV in localStorage

3. **Debounce detection:**
   - Don't re-detect on every DOM change
   - Use cooldown period

## Examples

### Example 1: MyPrize

```javascript
'myprize.us': {
    enabled: true,
    urlPattern: /\/play\//,
    selectors: {
        gameName: 'h1',  // Main heading has game name
        provider: null,  // Provider not in DOM, detect from API instead
    }
}
```

### Example 2: Multi-Selector

```javascript
'casino-site.com': {
    enabled: true,
    urlPattern: /\/games?\//,
    selectors: {
        // Try multiple possible selectors
        gameName: 'h1.game-title, .game-name, [data-game-name], #game-title',
        provider: '.provider, .developer, [data-provider]',
    }
}
```

### Example 3: Dynamic Detection

For sites with slow-loading content:

```javascript
function detectGameDelayed() {
    // Wait for game to load
    const checkInterval = setInterval(() => {
        const gameInfo = detectFromDOM(rules.selectors);
        if (gameInfo) {
            clearInterval(checkInterval);
            searchRTP(gameInfo);
        }
    }, 500);
    
    // Give up after 10 seconds
    setTimeout(() => clearInterval(checkInterval), 10000);
}
```

## Next Steps

1. **Test on multiple sites** - Visit different casino sites and check console
2. **Add site rules** - Create custom rules for your most-used sites
3. **Scrape more data** - Run SlotCatalog scraper for better coverage
4. **Share configurations** - Export working site rules for others

## Support

Check browser console for debug messages:
- `[RTP Finder] Initializing...`
- `[RTP Finder] Detected game: {...}`
- `[RTP Finder] Match found: {...}`
- `[RTP Finder] No RTP match found`
