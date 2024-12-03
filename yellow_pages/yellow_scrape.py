import logging
import os

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tqdm import tqdm
import time


# Set up the logger
def setup_logger(name="web_scraper", log_file="web_scraper.log", level=logging.INFO):
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add the formatter to the handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Usage
log_file_path = os.path.join(os.getcwd(), "web_scraper.log")
logger = setup_logger(log_file=log_file_path, level=logging.DEBUG)


class YellowPageScraper:
    def __init__(self, driver, url):
        self.driver = driver
        self.url = url
        self.driver.get(self.url)

    def get_business_name(self):
        business = self.driver.find_element(
            By.CSS_SELECTOR, "h1.dockable.business-name"
        ).text
        return business

    def get_address(self):
        address = self.driver.find_element(By.CSS_SELECTOR, "span.address").text
        return address

    def get_phone(self):
        phone = self.driver.find_element(By.CSS_SELECTOR, "a.phone.dockable").text
        return phone

    def get_email(self):
        email = self.driver.find_element(
            By.CSS_SELECTOR, "a.email-business"
        ).get_attribute("href")
        return email


def get_business_urls(search_driver, listing_url):
    search_driver.get(listing_url)
    scrollable_pane = search_driver.find_element(By.CSS_SELECTOR, "div.scrollable-pane")
    business_name_elements = scrollable_pane.find_elements(
        By.CLASS_NAME, "business-name"
    )
    href_values = [element.get_attribute("href") for element in business_name_elements]

    return href_values


pages = 1

# Path to your ChromeDriver
chromedriver_path = "YOUR CHROMEDRIVER PATH"

# Set up Selenium to use the ChromeDriver
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

url = "https://www.yellowpages.com/new-york-ny/auto-repair-service"
scraped_info = []

for i in range(pages):
    try:
        links = get_business_urls(driver, url)
    except Exception as e:
        logger.info(f"Getting business url filed for page {url} with error {e}")
        raise e

    for link in tqdm(links):
        current_info = {}
        yps = YellowPageScraper(driver, link)

        try:
            business_name = yps.get_business_name()
            current_info["business_name"] = business_name
        except Exception as e:
            logger.info(f"Business name extraction failed for {link}")
            current_info["business_name"] = None

        try:
            address = yps.get_address()
            current_info["address"] = address
        except Exception as e:
            logger.info(f"address extraction failed for {link}")
            current_info["address"] = None

        try:
            phone = yps.get_phone()
            current_info["phone"] = phone
        except Exception as e:
            logger.info(f"phone extraction failed for {link}")
            current_info["phone"] = None

        try:
            email = yps.get_email()
            current_info["email"] = email
        except Exception as e:
            logger.info(f"email extraction failed for {link}")
            current_info["email"] = None

        time.sleep(3)

        scraped_info.append(current_info)
    driver.get(url)
    next_page = driver.find_element(By.CSS_SELECTOR, "a.next.ajax-page")
    url = next_page.get_attribute("href")

scraped_df = pd.DataFrame(scraped_info)
scraped_df.to_csv("yellow_pages_scraped.csv")
