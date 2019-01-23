"""Scrape dam inventory."""
import queue
import threading
import logging
import csv
import os
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

PRIMARY_URL = "http://nid.usace.army.mil/cm_apex/f?p=838:4:0::NO"
TABLE_PATH = 'table.csv'
N_WORKERS = 4
N_RESULTS = 10000
SMALL_DELAY = 3.0
LARGE_DELAY = 25.0
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def search_state(work_queue, write_queue):
    """Search for state `state_code` and dumps result to `work_queue`."""
    firefox_options = Options()
    firefox_options.headless = True

    while True:
        state_code = work_queue.get()
        if state_code == 'STOP':
            break

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

        # make small number of searches so the next part goes faster
        driver.execute_script(f"javascript:gReport.search('SEARCH',1)")
        LOGGER.info('click search')
        time.sleep(SMALL_DELAY)

        # add all columns
        LOGGER.info("show column dialog")
        driver.execute_script(
            "javascript:gReport.dialog2('SHOW_COLUMN','COLUMN')")
        time.sleep(SMALL_DELAY)
        LOGGER.info("add all columns")
        driver.execute_script("javascript:g_Shuttlep_v01.move_all()")
        time.sleep(SMALL_DELAY)
        LOGGER.info("commit the column change")
        driver.execute_script("javascript:gReport.column.display()")
        time.sleep(SMALL_DELAY)

        search_link = driver.find_element_by_id('apexir_SEARCHDROPROOT')
        search_link.click()
        time.sleep(SMALL_DELAY)
        el = driver.find_element_by_id('apexir_columnsearch')
        el.find_element_by_id('STATE').click()
        LOGGER.info('click STATE')
        time.sleep(SMALL_DELAY)
        LOGGER.info(f'type {state_code}')
        input_box = driver.find_element_by_id('apexir_SEARCH')
        input_box.clear()
        input_box.send_keys(state_code)
        time.sleep(SMALL_DELAY)

        driver.execute_script(
            f"javascript:gReport.search('SEARCH',{N_RESULTS})")
        time.sleep(LARGE_DELAY)
        LOGGER.info(f'executed {state_code} {N_RESULTS} search')
        table_element = driver.find_element_by_xpath(
            "//table[@class='apexir_WORKSHEET_DATA']")
        bs_table_rows = BeautifulSoup(table_element.get_attribute(
            'outerHTML'), 'html.parser').select(
                'table.apexir_WORKSHEET_DATA tr')
        write_queue.put((bs_table_rows, state_code))
        #driver.save_screenshot(f"post_search_{state_code}.png")
        driver.close()


def writer(target_table_path, work_queue):
    """Writer worker, read `work_queue` for BS tables or 'STOP'."""
    if os.path.exists(TABLE_PATH):
        os.remove(TABLE_PATH)
    wrote_header = False
    with open(target_table_path, 'w', newline='') as table_file:
        csv_writer = csv.writer(
            table_file, delimiter=',', quotechar='"',
            quoting=csv.QUOTE_MINIMAL)
        while True:
            payload = work_queue.get()
            if payload == 'STOP':
                break
            bs_table_rows, state_code = payload
            for row_index, table_row in enumerate(bs_table_rows):
                if row_index % 100 == 0:
                    LOGGER.info(f'{state_code}, {row_index}')
                if not wrote_header:
                    row_element_text = [
                        col.text for col in table_row.find_all('th')]
                    wrote_header = True
                else:
                    row_element_text = [
                        col.text for col in table_row.find_all('td')]
                if row_element_text:
                    csv_writer.writerow(row_element_text)


def main():
    """Entry point."""
    thread_list = []
    work_queue = queue.Queue()
    write_queue = queue.Queue()

    for state_code in (
            'AZ', 'AL', 'AK', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI',
            'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI',
            'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
            'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
            'VT', 'VA', 'WA', 'WV', 'WI', 'WY'):
        work_queue.put(state_code)

    for _ in range(N_WORKERS):
        thread_list.append(
            threading.Thread(
                target=search_state, args=((work_queue, write_queue))))
        thread_list[-1].start()
        work_queue.put('STOP')

    write_thread = threading.Thread(
        target=writer, args=((TABLE_PATH, write_queue)))
    write_thread.start()

    for search_thread in thread_list:
        search_thread.join()
    write_queue.put('STOP')
    write_thread.join()


if __name__ == '__main__':
    main()
