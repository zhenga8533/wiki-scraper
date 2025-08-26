import os
import sys

from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util.constants import JOKER_URL
from util.core import download_images, get_html, save_json
from util.logger import Logger


def get_jokers(html: str, logger: Logger) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jokers = []
    base_url = "https://balatrowiki.org"

    heading = soup.find("span", id="List_of_Jokers")
    if not heading or not isinstance(heading, Tag):
        logger.error("Could not find the 'List of Jokers' heading.")
        return jokers

    table = heading.find_next("table", class_="sortable")
    if not table or not isinstance(table, Tag):
        logger.error("Could not find the main sortable jokers table.")
        return jokers

    tbody = table.find("tbody")
    if not tbody or not isinstance(tbody, Tag):
        logger.error("Could not find the table body.")
        return jokers

    rows = tbody.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) != 8:
            continue

        try:
            name_cell = cells[1].find_all("a")[-1]
            name = name_cell.get_text(strip=True) if name_cell else "N/A"

            img_tag = cells[1].find("img")
            img_src = img_tag.get("src") if img_tag else None
            full_img_url = f"{base_url}{img_src}" if img_src else None

            effect_cell = cells[2]
            effect = effect_cell.get_text(strip=True, separator=" ") if effect_cell else "N/A"

            joker_data = {
                "id": int(cells[0].get_text(strip=True)),
                "name": name,
                "image_url": full_img_url,
                "effect": effect,
                "cost": cells[3].get_text(strip=True),
                "rarity": cells[4].get_text(strip=True),
                "unlock": cells[5].get_text(strip=True),
                "type": cells[6].get_text(strip=True),
                "activation": cells[7].get_text(strip=True),
            }
            jokers.append(joker_data)
        except (AttributeError, IndexError, ValueError) as e:
            logger.error(f"Error parsing a row: {e}\nRow HTML: {row}")
            continue

    logger.info(f"Successfully scraped {len(jokers)} jokers.")
    return jokers


def main():
    load_dotenv()
    LOG = os.getenv("LOG") == "True"
    RETRIES = int(os.getenv("RETRIES", "3"))
    IMAGE_DIR = "joker_images"

    logger = Logger("Joker Scraper", "logs/joker_scraper.log", LOG)

    html = get_html(JOKER_URL, RETRIES, logger)
    if not html:
        logger.error("Failed to retrieve HTML. Exiting.")
        return

    jokers = get_jokers(html, logger)
    save_json(jokers, "jokers.json", logger)
    download_images(jokers, "image_url", "name", IMAGE_DIR, logger)


if __name__ == "__main__":
    main()
