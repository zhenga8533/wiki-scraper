import os
import sys

from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util.constants import DECK_URL
from util.core import download_images, get_html, save_json
from util.logger import Logger


def get_decks(html: str, logger: Logger) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    decks = []
    base_url = "https://balatrowiki.org"

    heading = soup.find("span", id="Decks")
    if not heading or not isinstance(heading, Tag):
        logger.error("Could not find the 'Decks' heading.")
        return decks

    table = heading.find_next("table", class_="sortable")
    if not table or not isinstance(table, Tag):
        logger.error("Could not find the main sortable decks table.")
        return decks

    tbody = table.find("tbody")
    if not tbody or not isinstance(tbody, Tag):
        logger.error("Could not find the table body.")
        return decks

    rows = tbody.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) != 4:
            continue

        try:
            name_cell = cells[1].find_all("a")[-1]
            name = name_cell.get_text(strip=True) if name_cell else "N/A"

            img_tag = cells[1].find("img")
            img_src = img_tag.get("src") if img_tag else None
            full_img_url = f"{base_url}{img_src}" if img_src else None

            description = cells[2].get_text(strip=True, separator=" ")
            unlock = cells[3].get_text(strip=True, separator=" ")

            deck_data = {
                "id": int(cells[0].get_text(strip=True)),
                "name": name,
                "image_url": full_img_url,
                "description": description,
                "unlock": unlock,
            }
            decks.append(deck_data)
        except (AttributeError, IndexError, ValueError) as e:
            logger.error(f"Error parsing a row: {e}\nRow HTML: {row}")
            continue

    logger.info(f"Successfully scraped {len(decks)} decks.")
    return decks


def main():
    load_dotenv()
    LOG = os.getenv("LOG") == "True"
    RETRIES = int(os.getenv("RETRIES", "3"))
    IMAGE_DIR = "assets/decks"

    logger = Logger("Deck Scraper", "logs/deck_scraper.log", LOG)

    html = get_html(DECK_URL, RETRIES, logger)
    if not html:
        logger.error("Failed to retrieve HTML. Exiting.")
        return

    decks = get_decks(html, logger)
    save_json(decks, "decks.json", logger)
    download_images(decks, "image_url", "name", IMAGE_DIR, logger)


if __name__ == "__main__":
    main()
