"""Scrape dam inventory."""
import logging
import csv
import os
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup

PRIMARY_URL = "http://nid.usace.army.mil/cm_apex/f?p=838:4:0::NO"
TABLE_PATH = 'table.csv'

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    if os.path.exists(TABLE_PATH):
        os.remove(TABLE_PATH)

    wrote_header = False
    for state_code in (
            'AZ', 'AL', 'AK', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI',
            'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI',
            'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
            'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
            'VT', 'VA', 'WA', 'WV', 'WI', 'WY'):

        firefox_options = Options()
        firefox_options.headless = True
        driver = webdriver.Firefox(options=firefox_options)
        driver.implicitly_wait(10)
        driver.get(PRIMARY_URL)

        el = driver.find_element_by_id('P12_ORGANIZATION')
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Academia':
                option.click()  # select() in earlier versions of webdriver
                LOGGER.info('clicked academia')
                break

        LOGGER.info('click NID Interactive Report')
        link = driver.find_element_by_link_text('NID Interactive Report')
        link.click()
        LOGGER.info('click search')
        time.sleep(0.1)
        driver.save_screenshot(f"screenshot_search_{state_code}.png")
        search_link = driver.find_element_by_id('apexir_SEARCHDROPROOT')
        search_link.click()
        time.sleep(0.1)
        driver.save_screenshot(f"screenshot_searchdropdown_{state_code}.png")
        el = driver.find_element_by_id('apexir_columnsearch')
        el.find_element_by_id('STATE').click()
        LOGGER.info('click STATE')
        time.sleep(0.1)
        driver.save_screenshot(f"screenshot_searchstate_{state_code}.png")
        LOGGER.info(f'type {state_code}')
        input_box = driver.find_element_by_id('apexir_SEARCH')
        input_box.clear()
        input_box.send_keys(state_code)
        driver.save_screenshot(f"screenshot_searchscode_{state_code}.png")
        time.sleep(0.1)
        driver.execute_script("javascript:gReport.search('SEARCH',100)")
        time.sleep(5.0)
        driver.save_screenshot(f"screenshot_searcch100_{state_code}.png")
        LOGGER.info('executed 100000 search')
        while True:
            try:
                table_element = driver.find_element_by_xpath(
                    "//table[@class='apexir_WORKSHEET_DATA']")
                bs_table_rows = BeautifulSoup(table_element.get_attribute(
                    'outerHTML'), 'html.parser').select(
                        'table.apexir_WORKSHEET_DATA tr')
                break
            except StaleElementReferenceException:
                LOGGER.info('stale element, trying again')
                time.sleep(0.5)
        driver.save_screenshot(f"screenshot_{state_code}.png")
        LOGGER.info("loaded table doc from a string")
        with open(TABLE_PATH, 'a', newline='') as table_file:
            csv_writer = csv.writer(
                table_file, delimiter=',', quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
            for row_index, table_row in enumerate(bs_table_rows):
                if not wrote_header:
                    csv_writer.writerow(
                        [col.text for col in table_row.find_all('th')])
                    wrote_header = True
                    continue
                if row_index % 100 == 0:
                    LOGGER.info(f'{state_code}, {row_index}')
                csv_writer.writerow(
                        [col.text for col in table_row.find_all('td')])
        driver.quit()
        break


if __name__ == '__main__':
    main()
