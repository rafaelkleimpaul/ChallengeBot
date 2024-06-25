import os
import re
import json
import uuid
import requests
import logging
import logging.config
from time import sleep
from datetime import datetime, timedelta
from RPA.Browser.Selenium import Selenium, By
from RPA.Excel.Files import Files
from robocorp.tasks import task

class Scraper:
    CUR_DIR = os.getcwd()
    OUT_DIR = f"{CUR_DIR}/output"
    PROP_FILE = f"{CUR_DIR}/properties.json"
    TODAY_STR = datetime.now().strftime("%m%d%Y")
    
    logging.config.dictConfig({"version": 1, "disable_existing_loggers": True})

    def __init__(self):
        self._init_dirs()
        logging.basicConfig(filename=f"{self.OUT_DIR}/LATIMES_{self.TODAY_STR}.log", level=logging.DEBUG, format="%(levelname)s %(asctime)s - %(message)s", filemode="a+")
        self.logger = logging.getLogger(__name__)
        self.log("info", "BOT started")

        self.props = self._load_props()
        self.URL = self.props.get("URL")
        self.SEARCH_TERM = self.props.get("SEARCH_PHRASE")
        self.TOPICS = self.props.get("TOPIC")
        self.MONTHS = self.props.get("NUMBER_OF_MONTHS", 1)
        self.DELAY = self.props.get("DELAY", 1)

    def log(self, level="debug", msg=""):
        print(f"{level.upper()}: {msg}")
        getattr(self.logger, level, self.logger.debug)(msg)

    def _init_dirs(self):
        for d in [self.OUT_DIR, f"{self.OUT_DIR}/images"]:
            if not os.path.exists(d):
                os.makedirs(d)

    def _load_props(self):
        try:
            with open(self.PROP_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.log("error", f"Cannot load data from JSON: {e}")
            return {}

    def open_browser(self):
        self.browser = Selenium(auto_close=False)
        self.browser.open_available_browser(self.URL)
        self.browser.maximize_browser_window()

    def search(self):
        self._click("//button[@data-element='search-button']")
        self._input("//input[@placeholder='Search']", self.SEARCH_TERM)
        self._click("//button[@data-element='search-submit-button']")

    def select_topics(self):
        if not self.TOPICS:
            return
        self._click("//div[1]/ps-toggler/ps-toggler/button[@class='button see-all-button']")
        for topic in self.TOPICS:
            try:
                self._click(f"//span[./text()='{topic}']/../input")
                sleep(self.DELAY)
            except Exception as e:
                self.log("error", f"Topic not found: {e}")

    def sort_by_newest(self):
        self._select_from_list("//select[@class='select-input']", "Newest")

    def next_page(self):
        try:
            self._click("//div[@class='search-results-module-next-page']/a")
            sleep(self.DELAY)
        except Exception as e:
            self.log("error", f"Error going to next page: {e}")

    def extract_data(self):
        data = [['DATE', 'TITLE', 'DESCRIPTION', 'IMAGE NAME', 'COUNT OF SEARCH TERMS', 'TITLE CONTAINS AMOUNT OF MONEY', 'DESCRIPTION CONTAINS AMOUNT OF MONEY']]
        flag = True
        while flag:
            news_elements = self.browser.get_webelements("//ul[@class='search-results-module-results-menu']/li")
            for elem in news_elements:
                date = self._timestamp_to_date(elem.find_element(By.CLASS_NAME, "promo-timestamp").get_attribute("data-timestamp"))
                title = elem.find_element(By.CLASS_NAME, "promo-title").text
                desc = elem.find_element(By.CLASS_NAME, "promo-description").text
                img_name = self._download_image(elem.find_element(By.CLASS_NAME, "image").get_attribute("src"))

                title_has_money = self._has_money(title)
                desc_has_money = self._has_money(desc)
                term_count = self._count_terms(self.SEARCH_TERM, title)

                if self._compare_date(date):
                    data.append([date, title, desc, img_name, self._count_terms(self.SEARCH_TERM, desc, term_count), title_has_money, desc_has_money])
                else:
                    flag = False
                    break
            if flag:
                self.next_page()
        self._save_to_excel(data)

    def _compare_date(self, date):
        start_date = datetime.now() - timedelta(days=30 * self.MONTHS)
        return datetime.strptime(date, "%m/%d/%Y") >= start_date

    @staticmethod
    def _timestamp_to_date(timestamp):
        return datetime.fromtimestamp(float(timestamp) / 1000).strftime("%m/%d/%Y")

    def _save_to_excel(self, data):
        lib = Files()
        lib.create_workbook()
        lib.append_rows_to_worksheet(data)
        lib.save_workbook(f"{self.OUT_DIR}/result.xlsx")

    def _download_image(self, url):
        if not url:
            return ""
        img_name = str(uuid.uuid4())
        img_data = requests.get(url).content
        with open(f"{self.OUT_DIR}/images/{img_name}.jpg", "wb") as f:
            f.write(img_data)
        return img_name

    @staticmethod
    def _count_terms(term, text, count=0):
        return sum(1 for word in text.split() if word.strip(",.;:-?!") == term) + count

    @staticmethod
    def _has_money(text):
        return bool(re.search(r"(\$\s*\d+.\d*.\d*|\d+\s*(dollars|usd|dollar))", text, re.IGNORECASE))

    def _click(self, xpath):
        self.browser.wait_until_page_contains_element(xpath, self.DELAY)
        self.browser.click_button_when_visible(xpath)

    def _input(self, xpath, text):
        self.browser.wait_until_page_contains_element(xpath, self.DELAY)
        self.browser.input_text(xpath, text)

    def _select_from_list(self, xpath, text):
        self.browser.wait_until_page_contains_element(xpath, self.DELAY)
        option_xpath = f"{xpath}/option[text()='{text}']"
        value = self.browser.get_element_attribute(option_xpath, "value")
        self.browser.select_from_list_by_value(xpath, value)
        sleep(self.DELAY)

@task
def main():
    bot = Scraper()
    bot.open_browser()
    bot.search()
    bot.select_topics()
    bot.sort_by_newest()
    bot.extract_data()
    bot.browser.close_browser()
    bot.log("info", "Bot execution finished")
