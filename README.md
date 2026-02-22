# TasteAtlas Scraper

Scrapes [tasteatlas.com](https://www.tasteatlas.com) to collect the featured food items for every country.

## Data

Results are stored in [`data/countries.json`](data/countries.json). Each country entry contains:

```json
"afghanistan": {
  "name": "Afghanistan",
  "tasteatlas_url": "https://www.tasteatlas.com/afghanistan",
  "continent": "Asia",
  "food": [
    {
      "name": "Manti",
      "category": "Dumplings",
      "tasteatlas_url": "https://www.tasteatlas.com/mantu-afghanistan",
      "image_url": "https://cdn.tasteatlas.com/...",
      "rating": 4.3,
      "location": "Afghanistan"
    }
  ]
}
```

## Usage

Install dependencies:

```bash
pip install playwright beautifulsoup4
playwright install chromium
```

Run the scraper:

```bash
python src/scrape.py
```

`countries.json` is updated incrementally, progress is saved after each country.
