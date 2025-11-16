"""
Test the SlotCatalog scraper on the example HTML file
"""
from scrape_slotcatalog import parse_game_page

# Read the example HTML
with open(r"c:\Users\sydne\Desktop\rtp-data\slotcatalog_html_example.html", 'r', encoding='utf-8') as f:
    html = f.read()

# Parse it
game_data = parse_game_page(html, "https://slotcatalog.com/en/slots/Alien-Robots")

# Display results
print("Test Results for Alien Robots:")
print("="*60)
print(f"Game Name: {game_data['game']}")
print(f"Publisher: {game_data['publisher']}")
print(f"Min RTP: {game_data['min_rtp']}")
print(f"Max RTP: {game_data['max_rtp']}")
print(f"Default RTP: {game_data['default_rtp']}")
print("="*60)

# Expected values based on the HTML
expected = {
    'game': 'Alien Robots',
    'publisher': 'NetEnt',
    'min_rtp': 96.3,
    'max_rtp': 96.6,
    'default_rtp': 96.6
}

# Validate
all_correct = True
for key, expected_value in expected.items():
    actual_value = game_data[key]
    match = actual_value == expected_value
    status = "✓" if match else "✗"
    print(f"{status} {key}: Expected '{expected_value}', Got '{actual_value}'")
    if not match:
        all_correct = False

print("="*60)
if all_correct:
    print("✓ All tests passed! Scraper is working correctly.")
else:
    print("✗ Some tests failed. Check the parsing logic.")
