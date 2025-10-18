import os
import re
import bz2

import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from loguru import logger
from playwright.sync_api import sync_playwright

load_dotenv()


def extract_data(response):
    dates = []
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", class_="csgo_scoreboard_inner_left")
    for t in table:
        text = str(t)

        pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} GMT"
        datetime_match = re.search(pattern, text)
        dates.append(datetime_match.group())
    return dates


def generate_filename(dt: str):
    """."""
    filename = dt.replace("-", "_").replace(":", "_").replace(" ", "_")[:-7]
    return filename + ".dem.bz2"


def get_url(response):
    """."""
    urls = []
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a", href=True)
    for link in links:
        if "bz2" in link["href"]:
            url = str(link).split('"')[1]
            urls.append(url)

    return urls


def get_steamlogin_token():
    """Get Steam login token from .steamlogin file or environment variable."""
    # Try to read from .steamlogin file first
    if os.path.exists(".steamlogin"):
        try:
            with open(".steamlogin") as f:
                return f.readlines()[0].strip()
        except Exception as e:
            logger.warning(f"Failed to read .steamlogin: {e}")

    # Fallback to environment variable
    steam_token = os.getenv("steam_token")
    if steam_token:
        logger.info("Using steam_token from environment variable")
        return steam_token

    # No token found
    logger.error("Steam login token not found! Please provide .steamlogin file or set steam_token environment variable")
    exit(1)


def get_page():
    """."""

    # Get the latest Steamlogin
    steamLoginSecure = get_steamlogin_token()

    # url = "https://teamcommunity.com/id/pirez/gcpd/730?tab=matchhistorypremier"
    url = "https://steamcommunity.com/id/pirez/gcpd/730?tab=matchhistorypremier"
    cookies = {
        "sessionid": os.getenv("sessionid"),
        "cookieSettings": os.getenv("cookieSettings"),
        "broswerid": os.getenv("broswerid"),
        "steamLoginSecure": steamLoginSecure,  # os.getenv('steamLoginSecure'),
        "steamCountry": os.getenv("steamCountry"),
        "timezoneOffset": os.getenv("timezoneOffset"),
    }

    return requests.get(url, cookies=cookies)


def get_download_folder():
    """Get download folder from environment variable or use default .tmp/"""
    download_folder = os.getenv("download_folder")
    if not download_folder:
        download_folder = ".tmp"
        logger.info(f"download_folder not set, using default: {download_folder}")
    return download_folder


def download_file(url, fname, directory=None):
    if directory is None:
        directory = get_download_folder()
    logger.info(f"Downloading from {url}")
    if not os.path.exists(directory):
        os.makedirs(directory)

    response = requests.get(url)
    fout = os.path.join(directory, fname)

    logger.info(f"Saving {fname}")

    with open(fout, "wb") as file:
        file.write(response.content)
    logger.info(f"Downloaded {fout}")


def unpack_file(fname, directory):
    bz2_file_path = os.path.join(directory, fname)
    output_file_path = os.path.join(directory, fname.replace(".bz2", ""))
    with bz2.BZ2File(bz2_file_path, "rb") as file:
        # Decompress the content
        decompressed_data = file.read()

        # Write the decompressed content to a new file
        with open(output_file_path, "wb") as output_file:
            output_file.write(decompressed_data)

        os.remove(bz2_file_path)


def etl():
    logger.info("Starting...")
    directory = get_download_folder()
    response = get_page()
    urls = get_url(response)

    if len(urls) == 0:
        # Try to identify a button called  "LOAD MORE HISTORY" and click it
        logger.info("Trying to load more history...")
        soup = BeautifulSoup(response.content, "html.parser")
        # dump the content to a file for debugging
        with open("debug_page.html", "w") as f:
            f.write(str(soup))
        # Use Playwright to click the "LOAD MORE HISTORY" button if present
        try:
            logger.info("Trying to use Playwright to load more history...")
            with sync_playwright() as p:
                steamLoginSecure = get_steamlogin_token()

                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set cookies for authentication BEFORE navigating to the page
                cookies = []
                cookie_data = [
                    ("sessionid", os.getenv("sessionid")),
                    ("cookieSettings", os.getenv("cookieSettings")),
                    ("broswerid", os.getenv("broswerid")),
                    ("steamLoginSecure", steamLoginSecure),
                    ("steamCountry", os.getenv("steamCountry")),
                    ("timezoneOffset", os.getenv("timezoneOffset")),
                ]
                
                for name, value in cookie_data:
                    if value is not None:  # Only add cookies with valid values
                        cookies.append({
                            "name": name,
                            "value": str(value),  # Ensure value is a string
                            "domain": ".steamcommunity.com",
                            "path": "/"
                        })
                
                page.context.add_cookies(cookies)
                page.goto("https://steamcommunity.com/id/pirez/gcpd/730?tab=matchhistorypremier")
                
                # Wait for the page to fully load
                page.wait_for_load_state("networkidle")
                
                # Wait for the button and click it (can target either the link or the button)
                logger.info("Waiting for 'Load More History' button...")
                page.wait_for_selector("#load_more_clickable", timeout=10000)
                page.click("#load_more_clickable")
                
                # Wait for new content to load after clicking
                logger.info("Clicked button, waiting for new content...")
                page.wait_for_timeout(3000)  # Wait for new content to load
                page.wait_for_load_state("networkidle")
                
                html = page.content()
                browser.close()
                # Parse the new HTML for URLs
                soup = BeautifulSoup(html, "html.parser")
                urls = get_url(type("obj", (object,), {"content": html.encode("utf-8")})())
                # log the urls found
                logger.info(f"Found {len(urls)} URLs after loading more history.")
                
                # Extract dates from the new response
                response = type("obj", (object,), {"content": html.encode("utf-8")})()
        except Exception as e:
            logger.error(f"Playwright failed: {e}")

    if len(urls) == 0:
        logger.error("Login failed")
        exit(1)
    dates = extract_data(response)
    for url, dt in zip(urls[:], dates[:]):
        fname = generate_filename(dt)

        if not os.path.exists(os.path.join(directory, fname.replace(".bz2", ""))):
            download_file(url, fname, directory)
            unpack_file(fname, directory)
            logger.info(f"Done with {fname}")
        else:
            logger.warning(f"File exists ({fname}), skipping")


if __name__ == "__main__":
    directory = get_download_folder()

    etl()
    for f in os.listdir(directory):
        try:
            if f.endswith("bz2"):
                unpack_file(f, directory)
        except:
            logger.error(f"{f} unpacking went wrong")
    pass
