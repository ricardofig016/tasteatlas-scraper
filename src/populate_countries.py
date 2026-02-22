import json
import re
from pathlib import Path


def extract_countries_from_html(html_content, continent):
    """
    Extract country information from HTML content.

    Args:
        html_content (str): The HTML content to parse
        continent (str): The continent name to associate with countries

    Returns:
        dict: Dictionary with country slugs as keys and country data as values
    """
    countries = {}

    # Pattern to match country entries: title="Country Name" and href="slug?ref=main-menu"
    pattern = r'title="([^"]+)">[^<]*<a[^>]*href="([^"?]+)'

    matches = re.finditer(pattern, html_content)

    for match in matches:
        country_name = match.group(1)
        country_slug = match.group(2)

        # Skip if no valid slug found
        if not country_slug:
            continue

        # Create the key from the slug (lowercase version for consistency)
        key = country_slug.lower().replace("-", "_")

        # Build the country data
        countries[key] = {"name": country_name, "tasteatlas_url": f"https://www.tasteatlas.com/{country_slug}", "continent": continent}

    return countries


def main():
    """Main script to read HTML files and populate countries.json"""

    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    country_anchors_dir = project_root / "data" / "country_anchors"
    countries_json = project_root / "data" / "countries.json"

    # Map of HTML filenames to continent names
    continent_mapping = {
        "africa.html": "Africa",
        "asia.html": "Asia",
        "australia.html": "Australia",
        "europe.html": "Europe",
        "north_america.html": "North America",
        "south_america.html": "South America",
    }

    all_countries = {}

    # Process each HTML file
    for html_file, continent in continent_mapping.items():
        file_path = country_anchors_dir / html_file

        if not file_path.exists():
            print(f"Warning: {file_path} not found")
            continue

        print(f"Processing {html_file}...")

        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        countries = extract_countries_from_html(html_content, continent)
        all_countries.update(countries)
        print(f"  Found {len(countries)} countries")

    # Sort by key for consistent output
    sorted_countries = dict(sorted(all_countries.items()))

    # Write to JSON file
    with open(countries_json, "w", encoding="utf-8") as f:
        json.dump(sorted_countries, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully populated {countries_json}")
    print(f"Total countries: {len(sorted_countries)}")


if __name__ == "__main__":
    main()
