import io
import json
import logging
import os
import re
from typing import Dict, List

import bs4
import requests
from PIL import Image

from util.logger import Logger


def download_images(items: List[Dict], url_key: str, name_key: str, save_dir: str, logger: Logger) -> None:
    """
    Download images from a list of items and save them as WebP files.

    :param items: A list of dictionaries containing image URLs and names.
    :param url_key: The key in the dictionary that contains the image URL.
    :param name_key: The key in the dictionary that contains the image name.
    :param save_dir: The directory to save the images to.
    :param logger: The logger to log with.
    :return: None
    """

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        logger.info(f"Created directory: {save_dir}")

    # Clear existing files in the directory
    for filename in os.listdir(save_dir):
        file_path = os.path.join(save_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                logger.debug(f"Deleted existing file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")

    # Download and save images
    for item in items:
        image_url = item.get(url_key)
        name = item.get(name_key)

        if not image_url or not name:
            logger.warning(f"Missing URL or name for item: {item}")
            continue

        try:
            with requests.get(image_url) as r:
                r.raise_for_status()
                image_bytes = r.content

            with Image.open(io.BytesIO(image_bytes)) as img:
                sanitized_name = re.sub(r'[\\/*?:"<>|]', "", name)
                filename = f"{sanitized_name}.webp"
                file_path = os.path.join(save_dir, filename)

                img.save(file_path, "webp")

            logger.debug(f"Successfully downloaded and saved {name} as WebP.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download image for {name}: {e}")
        except IOError as e:
            logger.error(f"Failed to process or save image for {name}: {e}")

    logger.info("Finished downloading images.")


def get_html(url: str, retries: int, logger: Logger) -> str:
    """
    Get the HTML from a URL.

    :param url: The URL to get the HTML from.
    :param retries: The number of retries to try getting the HTML.
    :param logger: The logger to log with.
    :return: The HTML from the URL.
    """

    for i in range(retries):
        try:
            logger.log(logging.INFO, f"Attempt {i + 1}: Getting HTML from {url}")
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Attempt {i + 1}: Failed to get HTML from {url}")
            logger.error(e.__str__())

    logger.error(f"Failed to get HTML from {url} after {retries} attempts")
    exit(1)


def save_html(html: str, file_name: str, logger: Logger):
    """
    Save HTML to a file.

    :param html: The HTML to save.
    :param file_name: The path to save the HTML to.
    :param logger: The logger to log with.
    :return: None
    """

    logger.log(logging.INFO, f"Formatting HTML to save to {file_name}")
    soup = bs4.BeautifulSoup(html, "html.parser")
    pretty_html = soup.prettify()

    logger.log(logging.INFO, f"Saving HTML to {file_name}")
    try:
        os.makedirs("html", exist_ok=True)
        with open(f"html/{file_name}", "w", encoding="utf-8") as file:
            file.write(pretty_html)
            logger.log(logging.INFO, f"Saved HTML to {file_name}")
    except Exception as e:
        logger.error(f"Failed to save HTML to {file_name}")
        logger.error(e.__str__())


def save_json(data: dict | list, file_name: str, logger: Logger):
    """
    Save JSON to a file.

    :param data: The JSON to save.
    :param file_name: The path to save the JSON to.
    :param logger: The logger to log with.
    :return: None
    """

    logger.log(logging.INFO, f"Saving JSON to {file_name}")
    try:
        os.makedirs("json", exist_ok=True)
        with open(f"json/{file_name}", "w") as file:
            json.dump(data, file, indent=4)
            logger.log(logging.INFO, f"Saved JSON to {file_name}")
    except Exception as e:
        logger.error(f"Failed to save JSON to {file_name}")
        logger.error(e.__str__())
