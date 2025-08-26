import os
import sys

from bs4 import BeautifulSoup
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util.constants import TEMPLATE_URL
from util.core import get_html, save_json
from util.logger import Logger


def get_test(html: str, retries: int, logger: Logger) -> list[dict]:
    """Extract test data from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    tests = []

    # Example extraction logic (to be customized)
    for item in soup.select(".test-item"):
        test_name_elem = item.select_one(".test-name")
        test_value_elem = item.select_one(".test-value")
        test = {
            "name": test_name_elem.get_text(strip=True) if test_name_elem else "",
            "value": test_value_elem.get_text(strip=True) if test_value_elem else "",
        }
        tests.append(test)

    logger.info(f"Extracted {len(tests)} tests.")
    return tests


def main():
    # Load environment variables
    load_dotenv()
    LOG = os.getenv("LOG") == "True"
    RETRIES = int(os.getenv("RETRIES", "3"))

    # Initialize logger
    logger = Logger("Template Scraper", "logs/template_scraper.log", LOG)

    # Scrape
    html = get_html(TEMPLATE_URL, RETRIES, logger)
    template = get_test(html, RETRIES, logger)
    save_json(template, "template.json", logger)


if __name__ == "__main__":
    main()
