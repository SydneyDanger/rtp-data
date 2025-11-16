# Tampermonkey RTP Fetcher - Updates

## What Was Fixed

The script was failing to match games because:

1. **Provider Code Mismatch**: The JSON uses short provider codes (`relax`, `hacksaw`, `evolution`) while the CSV uses full names (`Relax Gaming`, `Hacksaw Gaming`, `Red Tiger Gaming`)

2. **Studio Field Ignored**: For Evolution-aggregated games, the actual developer is in the `studio` field (e.g., `red_tiger`, `nolimit_city`), not the `provider` field

3. **No Fallback Matching**: Only exact matches were attempted

## Changes Made

### 1. Provider/Studio Mapping
Added a `PROVIDER_MAP` that translates JSON codes to CSV publisher names:
- `relax` → `Relax Gaming`
- `evolution` + `studio: red_tiger` → `Red Tiger Gaming`  
- `evolution` + `studio: nolimit_city` → `Nolimit City`
- `bgaming` → `BGaming`
- `hacksaw` → `Hacksaw Gaming`
- etc.

### 2. Multi-Strategy Matching
The script now tries three strategies in order:
1. **Exact match**: Game name + expected publisher both match exactly
2. **Family match**: Game name matches exactly, publisher shares words with expected publisher
3. **Fuzzy match**: Game name partially matches (contains/contained by) with correct publisher

### 3. Better UI Feedback
- Shows provider/studio in format: `hacksaw/hacksaw_gaming`
- Displays which publisher it's looking for when no match found
- Summary at top shows: `X / Y matched (Z%)`
- Console logging for debugging each match attempt

### 4. RTP Priority
Changed RTP display priority to: `default_rtp` → `max_rtp` → `min_rtp`

## Important Note

**Many games in your example JSON don't exist in the CSV**, specifically:
- All Hacksaw Gaming games (not in CasinoListings CSV)
- All Booming Games (not in CasinoListings CSV)
- Most newer/specific game titles

The CSV appears to be from CasinoListings.com which has ~2,896 games but may not include:
- Newer releases
- Games from certain providers (Hacksaw, Booming, Backseat Gaming)
- Specific variants of games

## Testing

To test with games that ARE in the CSV, look for games from:
- **Relax Gaming**: Money Cart, Money Cart 2, Book of 99, Epic Joker, Wild Chapo
- **Red Tiger Gaming**: 777 Super Strike, Mystery Reels Megaways, Dragon Pearl
- **Nolimit City**: Bushido Ways xNudge (NOT in CSV), Oktoberfest, Hot Nudge, Tombstone
- **BGaming**: Domintors Deluxe, Fruit Million, Elvis Frog in Vegas

## Console Output

Open browser DevTools → Console to see:
```
[RTP Match] Searching for: "Le Zeus" | Provider: hacksaw | Studio: hacksaw_gaming | Expected CSV Publisher: Hacksaw Gaming
[RTP Match] ✗ No match found for "Le Zeus"
```

This will help you understand why specific games don't match.
