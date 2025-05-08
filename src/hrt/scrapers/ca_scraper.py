"""CA scraper."""

from typing import Dict, List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from hrt.common.config_reader import logger
from hrt.common.constants import LOAD_WAIT_TIME, SEARCH_WAIT_TIME
from hrt.common.enums import CountryCode
from hrt.common.utils import select_from_options
from hrt.scrapers.base_scraper import BaseScraper


def select_option(element, prompt: str) -> None:
    options = element.find_elements(By.TAG_NAME, "option")
    # read <option value="VA2">VA2 - Quebec</option> and get the value
    options_list: Dict[str, str] = {}
    for option in options:
        option_text = option.text
        option_value = option.get_attribute("value")
        options_list[option_text] = option_value
    selected_option = select_from_options(options_list, prompt)
    if selected_option:
        element.send_keys(selected_option)
    else:
        logger.error("No option selected.")
        element.send_keys("")


class CAScraper(BaseScraper):
    def __init__(self, driver: str, app_config: Optional[Dict] = None):
        super().__init__(driver, CountryCode.CANADA, app_config)

    def download_assigned_callsigns(self, url: str, output_file_path: str) -> None:
        from hrt.common.utils import download_zip_file

        download_zip_file(url, output_file_path)

    def download_available_callsigns(self, url: str, output_file_path: str) -> List[str]:
        callsigns: List[str] = []

        try:
            self.driver.get(url)

            wait = WebDriverWait(self.driver, LOAD_WAIT_TIME)
            wait.until(ec.presence_of_element_located((By.ID, "P_PREFIX_U")))

            # select prefix
            prefix_input = self.driver.find_element(By.ID, "P_PREFIX_U")
            select_option(prefix_input, "Province")

            # select suffix characters
            for i in range(1, 4):
                suffix_input = self.driver.find_element(By.ID, f"P_SUFFIX_CHAR_{i}_U")
                valid_suffix = False
                while not valid_suffix:
                    suffix = input(f"Enter the Suffix Character {i} (A-Z or All): ")
                    if suffix == "All" or (
                        len(suffix) == 1 and suffix.isalpha() and suffix.isupper()
                    ):
                        valid_suffix = True
                        suffix_input.send_keys(suffix)
                    else:
                        print("Invalid suffix. Please try again.")

            # select suffix type
            suffix_type_input = self.driver.find_element(By.ID, "P_SUFFIX_TYPE_U")
            select_option(suffix_type_input, "Suffix")

            # send the form, search for input with type submit and value Search
            search_button = self.driver.find_element(
                By.XPATH, "//input[@type='submit' and @value='Search']"
            )
            search_button.click()

            # wait for the search results to load
            wait = WebDriverWait(self.driver, SEARCH_WAIT_TIME)
            wait.until(ec.presence_of_element_located((By.CLASS_NAME, "sdContent")))
            if "No such call sign is available." in self.driver.page_source:
                logger.info("No call signs found.")
                return callsigns
            # read the count of call signs found under a <p> tag under the <div>
            # with class "sdContent"
            count_text = (
                self.driver.find_element(By.CLASS_NAME, "sdContent")
                .find_element(By.TAG_NAME, "p")
                .text
            )
            logger.debug(count_text)
            count = int(count_text.split()[4])
            logger.info("Found %d callsigns", count)
            # table = self.driver.find_element(By.XPATH,
            # "//table[.//caption[text()='Search Results']]")
            table = self.driver.find_element(By.XPATH, "//table[.//th[text()='Call Sign']]")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                logger.debug(row.text)
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 0:
                    callsign = cells[0].text
                    callsigns.append(callsign)

            # match the callsigns count with the count displayed on the page
            if len(callsigns) != count:
                logger.warning(
                    "Count mismatch. Found %d callsigns, but the page displayed %d callsigns.",
                    len(callsigns),
                    count,
                )

            with open(output_file_path, "w", encoding="utf-8") as file:
                for callsign in callsigns:
                    file.write(f"{callsign}\n")
                logger.info("Callsigns saved to %s", output_file_path)
            return callsigns

        finally:
            self.driver.quit()
