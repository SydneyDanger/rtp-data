# RTP Finder - API Adapter Guide

## Overview

The adapter-based RTP finder intercepts API calls that sites make when loading games. This is **much more reliable** than DOM parsing because:

1. **Consistent Data** - APIs return structured JSON
2. **Provider Info** - APIs include accurate provider/studio data
3. **Early Detection** - Catches game before page fully renders
4. **No DOM Changes** - Unaffected by UI redesigns

## How It Works

```
Page loads → Widget appears (collapsed) → Shows adapter status → Game API call → 
Intercept → Parse JSON → Match RTP → Auto-expand widget
```

The script intercepts both `fetch()` and `XMLHttpRequest` calls, checks if they match configured API patterns, extracts game info, and displays RTP data.

### Widget Behavior

- **Always visible** - Shows up in the corner on all sites
- **Collapsed state** - Shows adapter status (active or not)
- **Auto-expands** - When a game is detected via API
- **Manual toggle** - Click to expand/collapse at any time

### Widget States

**Collapsed - Adapter Active (MyPrize.us)**
```
┌─────────────────┐
│ ✓  RTP FINDER   │
│    MyPrize      │
└─────────────────┘
```

**Collapsed - No Adapter (Other Sites)**
```
┌─────────────────┐
│ ○  RTP FINDER   │
│    No Adapter   │
└─────────────────┘
```

**Expanded - Waiting for Game**
```
┌───────────────────────────┐
│ RTP FINDER          [API] │
│                           │
│    Adapter Active         │
│       MyPrize             │
│   Waiting for game...     │
│                           │
│    Click to collapse      │
└───────────────────────────┘
```

**Expanded - Game Detected**
```
┌───────────────────────────┐
│ RTP FINDER          [API] │
│                           │
│ Epic Joker                │
│ Relax Gaming              │
│                           │
│ ┌─────────────────────┐   │
│ │ RTP:      96.50%    │   │
│ │ Range: 96.14-96.5%  │   │
│ │ Source: Relax Gaming│   │
│ └─────────────────────┘   │
│                           │
│    Click to collapse      │
└───────────────────────────┘
```

## MyPrize Adapter Example

```javascript
'myprize.us': {
    name: 'MyPrize',
    enabled: true,
    
    // API endpoints to intercept
    apiPatterns: [
        /\/api\/player\/games\/slug\//,
        /\/api\/igames\/mission\//
    ],
    
    // Extract game info from API response
    parseResponse: (data) => {
        if (Array.isArray(data)) {
            // Mission API returns array
            return data.map(game => ({
                name: game.name,
                provider: game.provider,
                studio: game.studio || game.provider
            }));
        } else {
            // Slug API returns single game
            return {
                name: data.name,
                provider: data.provider,
                studio: data.studio || data.provider
            };
        }
    }
}
```

## Adding a New Site Adapter

### Step 1: Find the API Endpoint

1. Open DevTools (F12) → Network tab
2. Navigate to a game on the site
3. Look for API calls that return game data
4. Note the URL pattern and response structure

**Example:**
```
Request: GET /api/games/12345
Response: {
  "id": 12345,
  "title": "Starburst",
  "developer": "NetEnt",
  ...
}
```

### Step 2: Create the Adapter

```javascript
'example-casino.com': {
    name: 'Example Casino',
    enabled: true,
    
    // Regex patterns for API URLs
    apiPatterns: [
        /\/api\/games\/\d+/,           // Match /api/games/12345
        /\/v1\/casino\/game-info/      // Match versioned API
    ],
    
    // Parse the JSON response
    parseResponse: (data) => {
        return {
            name: data.title,              // Game name
            provider: data.developer,      // Provider
            studio: data.studio            // Optional studio
        };
    }
}
```

### Step 3: Test

1. Add adapter to `ADAPTERS` object
2. Reload Tampermonkey script
3. Visit a game page
4. Check console for `[RTP Finder]` messages
5. Widget should appear with RTP data

## Adapter Configuration

### Required Fields

```javascript
{
    name: 'Site Name',           // Display name for logging
    enabled: true,               // Toggle adapter on/off
    apiPatterns: [],             // Array of regex patterns to match URLs
    parseResponse: (data) => {}  // Function to extract game info from JSON
}
```

### API Patterns

Use regex to match API endpoints:

```javascript
apiPatterns: [
    /\/api\/games\//,              // Simple path match
    /\/api\/v\d+\/games/,          // Versioned API
    /game-info\?id=\d+/,           // Query parameter
    /\/slots\/[a-z0-9-]+\/data/    // Slug-based endpoint
]
```

### Parse Response Function

Return an object with these fields:

```javascript
parseResponse: (data) => {
    return {
        name: '',      // REQUIRED: Game name
        provider: '',  // REQUIRED: Provider/developer
        studio: ''     // OPTIONAL: Studio (for aggregators like Evolution)
    };
}
```

**Can also return an array** for endpoints that return multiple games:

```javascript
parseResponse: (data) => {
    return data.games.map(game => ({
        name: game.name,
        provider: game.provider,
        studio: game.studio
    }));
}
```

## Real-World Examples

### Example 1: Nested JSON Structure

```javascript
// API Response:
{
  "success": true,
  "data": {
    "game": {
      "name": "Book of Dead",
      "vendor": {
        "id": 12,
        "name": "Play'n GO"
      }
    }
  }
}

// Adapter:
parseResponse: (data) => {
    return {
        name: data.data.game.name,
        provider: data.data.game.vendor.name,
        studio: data.data.game.vendor.name
    };
}
```

### Example 2: Multiple Providers

```javascript
// API Response:
{
  "title": "Dragon Pearl",
  "gameProvider": "Evolution",
  "actualDeveloper": "Red Tiger"
}

// Adapter:
parseResponse: (data) => {
    return {
        name: data.title,
        provider: data.gameProvider,
        studio: data.actualDeveloper  // Important for Evolution games!
    };
}
```

### Example 3: Array of Games

```javascript
// API Response:
{
  "featured_games": [
    {"name": "Game 1", "provider": "NetEnt"},
    {"name": "Game 2", "provider": "Pragmatic Play"}
  ]
}

// Adapter:
parseResponse: (data) => {
    return data.featured_games.map(game => ({
        name: game.name,
        provider: game.provider,
        studio: game.provider
    }));
}
```

### Example 4: URL Parameters

```javascript
// API Call: /api/game?slug=starburst&provider=netent

// Adapter:
apiPatterns: [
    /\/api\/game\?/  // Match query string
],
parseResponse: (data) => {
    // If API doesn't return game info, extract from URL
    const url = new URL(data.url || window.location.href);
    return {
        name: data.name || url.searchParams.get('slug'),
        provider: data.provider || url.searchParams.get('provider'),
        studio: data.provider || url.searchParams.get('provider')
    };
}
```

## Debugging

### Enable Debug Mode

Set `DEBUG = true` in the script configuration.

### Console Messages

```javascript
[RTP Finder] Initializing for MyPrize...
[RTP Finder] Loaded 2896 games
[RTP Finder] Intercepted API call: https://myprize.us/api/player/games/slug/epic-joker
[RTP Finder] API Response: {name: "Epic Joker", provider: "relax", ...}
[RTP Finder] Processing game: {name: "Epic Joker", provider: "relax", ...}
[RTP Finder] Searching for: "Epic Joker" | Provider: relax | Studio: relax_gaming
[RTP Finder] ✓ Strategy 1 (Exact): Matched "Epic Joker" by Relax Gaming
[RTP Finder] RTP Match found: {game: "Epic Joker", publisher: "Relax Gaming", ...}
```

### Common Issues

#### Issue: No API calls intercepted

**Check:**
- Is `apiPatterns` regex correct?
- View Network tab to see actual API URLs
- Try broader pattern: `/\/api\//`

**Solution:**
```javascript
apiPatterns: [
    /./  // Temporarily match ALL requests (will be noisy!)
]
```

#### Issue: Parse error

**Check console for error message:**
```
[RTP Finder] Parse error: Cannot read property 'name' of undefined
```

**Solution:** Add safety checks:
```javascript
parseResponse: (data) => {
    if (!data || !data.game) return null;
    
    return {
        name: data.game?.name || 'Unknown',
        provider: data.game?.provider || 'Unknown',
        studio: data.game?.studio || data.game?.provider
    };
}
```

#### Issue: Widget shows wrong game

**Problem:** Multiple API calls happening

**Solution:** Add more specific patterns:
```javascript
apiPatterns: [
    /\/api\/games\/\d+$/,  // Only exact ID matches
    /\/api\/current-game/  // Only "current game" endpoint
]
```

## Advanced Features

### Conditional Parsing

```javascript
parseResponse: (data) => {
    // Different response formats based on endpoint
    if (data.type === 'single_game') {
        return {
            name: data.game.title,
            provider: data.game.vendor
        };
    } else if (data.type === 'game_list') {
        return data.items.map(item => ({
            name: item.name,
            provider: item.dev
        }));
    }
    return null;
}
```

### Custom Provider Mapping

If a site uses non-standard provider codes:

```javascript
parseResponse: (data) => {
    const providerMap = {
        'nt': 'NetEnt',
        'pp': 'Pragmatic Play',
        'png': "Play'n GO"
    };
    
    return {
        name: data.name,
        provider: providerMap[data.vendorCode] || data.vendorCode,
        studio: providerMap[data.vendorCode] || data.vendorCode
    };
}
```

### Delayed Processing

For sites where API fires before DOM ready:

```javascript
parseResponse: (data) => {
    // Wait for DOM
    setTimeout(() => {
        // Process game info
    }, 1000);
    
    return {
        name: data.name,
        provider: data.provider,
        studio: data.studio
    };
}
```

## Testing Checklist

- [ ] Widget appears immediately on page load (collapsed)
- [ ] Collapsed state shows correct adapter status
- [ ] Manual click expands widget
- [ ] Manual click collapses widget again
- [ ] API calls are intercepted (check console)
- [ ] Game info is parsed correctly
- [ ] Provider/studio mapping works
- [ ] Widget auto-expands when game detected
- [ ] RTP match found (when game exists in CSV)
- [ ] Widget displays correct game information
- [ ] Works on multiple games
- [ ] No console errors

## Provider Mapping

The script includes built-in provider mapping for common codes:

```javascript
"relax" → "Relax Gaming"
"netent" → "Net Entertainment"
"pragmatic" → "Pragmatic Play"
"evolution" → "Evolution Gaming"
// ... etc
```

Add more mappings in the `PROVIDER_MAP` object.

## Performance

**Minimal overhead:**
- Only intercepts requests on configured sites
- Only processes matching API patterns
- CSV loaded once at startup
- Async operations don't block page

**Memory usage:**
- CSV data: ~500KB (2,896 games)
- Widget: Minimal DOM elements
- No polling or intervals

## Benefits vs DOM Parsing

| Feature | API Adapter | DOM Parsing |
|---------|-------------|-------------|
| Reliability | ✓ Very High | △ Medium |
| Provider Data | ✓ Accurate | △ Often missing |
| Detection Speed | ✓ Immediate | △ After render |
| Site Updates | ✓ Resistant | ✗ Breaks often |
| Setup Complexity | △ Requires API research | ✓ Simple selectors |

## Next Steps

1. Test on MyPrize - should work immediately
2. Add adapters for other sites you use
3. Share adapters with community
4. Consider contributing back to improve coverage
