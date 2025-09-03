import os
import sys

from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util.constants import HANDS_URL
from util.core import get_html, save_json
from util.logger import Logger


def get_hands(html: str, logger: Logger) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    hands = []
    hand_sections = {
        "Regular_Poker_Hands": "regular",
        "Secret_Poker_Hands": "secret",
    }

    for heading_id, hand_type in hand_sections.items():
        heading = soup.find("span", id=heading_id)
        if not heading or not isinstance(heading, Tag):
            logger.error(f"Could not find the '{heading_id}' heading.")
            continue

        table = heading.find_next("table", class_="wikitable")
        if not table or not isinstance(table, Tag):
            logger.error(f"Could not find the table for '{heading_id}'.")
            continue

        tbody = table.find("tbody")
        if not tbody or not isinstance(tbody, Tag):
            logger.error(f"Could not find the table body for '{heading_id}'.")
            continue

        rows = tbody.find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            if len(cells) != 4:
                continue

            try:
                name = cells[0].get_text(strip=True)
                scoring_text = cells[1].get_text(strip=True, separator=" ")
                description = cells[2].get_text(strip=True, separator=" ")

                parts = scoring_text.split(" x ")
                chips = int(parts[0].split(" ")[0])
                mult = int(parts[1].split(" ")[0])

                hand_data = {
                    "name": name,
                    "type": hand_type,
                    "chips": chips,
                    "mult": mult,
                    "description": description,
                }
                hands.append(hand_data)
            except (AttributeError, IndexError, ValueError) as e:
                logger.error(f"Error parsing a row: {e}\nRow HTML: {row}")
                continue

    logger.info(f"Successfully scraped {len(hands)} poker hands.")
    return hands


def main():
    load_dotenv()
    LOG = os.getenv("LOG") == "True"
    RETRIES = int(os.getenv("RETRIES", "3"))

    logger = Logger("Poker Hand Scraper", "logs/poker_hand_scraper.log", LOG)

    html = get_html(HANDS_URL, RETRIES, logger)
    if not html:
        logger.error("Failed to retrieve HTML. Exiting.")
        return

    hands = get_hands(html, logger)
    save_json(hands, "hands.json", logger)


if __name__ == "__main__":
    main()
