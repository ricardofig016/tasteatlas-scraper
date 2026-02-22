import json
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

TASTEATLAS_BASE = "https://www.tasteatlas.com"
DATA_FILE = Path(__file__).parent.parent / "data" / "countries.json"


def parse_food_cards(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    foods = []

    for card in soup.select(".card.food"):
        # Name & food page URL
        h6 = card.select_one(".card__details h6")
        if not h6:
            continue
        name = h6.get_text(strip=True)
        food_link = h6.find_parent("a")
        food_url = TASTEATLAS_BASE + food_link["href"] if food_link else None

        # Category label (e.g. "Dumplings", "Bread")
        label_el = card.select_one(".card__label")
        category = label_el.get_text(strip=True) if label_el else None

        # Image (absent when the card has no photo)
        img_el = card.select_one(".card__visual img")
        image_url = img_el["src"] if img_el else None

        # Rating ("n/a" → None)
        rating_el = card.select_one(".card__info-value")
        rating_text = rating_el.get_text(strip=True) if rating_el else None
        try:
            rating = float(rating_text)
        except (TypeError, ValueError):
            rating = None

        # Location (may include city, e.g. "Kabul, Afghanistan")
        location_el = card.select_one(".card__location a.fw-600")
        location = location_el.get_text(strip=True) if location_el else None

        foods.append(
            {
                "name": name,
                "category": category,
                "tasteatlas_url": food_url,
                "image_url": image_url,
                "rating": rating,
                "location": location,
            }
        )

    return foods


def scrape_country(page, country_key: str, country_data: dict) -> list[dict]:
    url = country_data["tasteatlas_url"]
    print(f"Scraping {country_data['name']} ({url}) ...")

    page.goto(url, wait_until="domcontentloaded", timeout=60_000)

    try:
        page.wait_for_selector("#list-food-must-try", timeout=45_000)
    except Exception:
        debug_path = Path(__file__).parent.parent / "debug_page.html"
        debug_path.write_text(page.content(), encoding="utf-8")
        print(f"  ! #list-food-must-try not found. Page saved to {debug_path}")
        return []

    html = page.inner_html("#list-food-must-try")
    return parse_food_cards(html)


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/131.0.0.0 Safari/537.36"),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for i, key in enumerate(data.keys(), 1):
            foods = scrape_country(page, key, data[key])
            data[key]["food"] = foods
            print(f"  → [{i}/{len(data)}] {len(foods)} food items found for {data[key]['name']}")
            # Save after every country so progress isn't lost on failure
            DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

        browser.close()

    print("Done. countries.json updated.")


if __name__ == "__main__":
    main()
