import csv
from bs4 import BeautifulSoup

INPUT_PATH = r"c:\\Users\\sydne\\Desktop\\rtp-data\\casinolistings_rtp.txt"
OUTPUT_PATH = r"c:\\Users\\sydne\\Desktop\\rtp-data\\rtp_data.csv"


def parse_float_or_none(text: str | None):
    """Convert a percentage string like '96.5%' to float 96.5, or None if empty/invalid."""
    if text is None:
        return None
    cleaned = text.strip().replace("%", "")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def main() -> None:
    # Read the saved HTML file
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Find the slots RTP table
    table = soup.find("table", {"id": "slots", "class": "games lister"})
    if table is None:
        raise RuntimeError("Could not find RTP table with id='slots' in the HTML")

    tbody = table.find("tbody")
    if tbody is None:
        raise RuntimeError("RTP table has no <tbody> section")

    rows = tbody.find_all("tr")
    records: list[dict[str, object]] = []

    for row in rows:
        cells = row.find_all("td")
        # Expecting 5 data columns: Game, Publisher, Min, Max, Default
        if len(cells) < 5:
            continue

        game = cells[0].get_text(strip=True)
        publisher = cells[1].get_text(strip=True)
        min_rtp = parse_float_or_none(cells[2].get_text())
        max_rtp = parse_float_or_none(cells[3].get_text())
        default_rtp = parse_float_or_none(cells[4].get_text())

        records.append(
            {
                "game": game,
                "publisher": publisher,
                "min_rtp": min_rtp,
                "max_rtp": max_rtp,
                "default_rtp": default_rtp,
            }
        )

    # Write all records to CSV with no filtering
    fieldnames = ["game", "publisher", "min_rtp", "max_rtp", "default_rtp"]
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Wrote {len(records)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
