"""Scrape dam inventory."""
import os
import time

from selenium import webdriver

PRIMARY_URL = "http://nid.usace.army.mil/cm_apex/f?p=838:4:0::NO"
TABLE_PATH = 'table.csv'


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

        driver = webdriver.PhantomJS()
        driver.get(PRIMARY_URL)

        driver.save_screenshot(f"screenshot_{state_code}.png")
        el = driver.find_element_by_id('P12_ORGANIZATION')
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Academia':
                option.click()  # select() in earlier versions of webdriver
                print('clicked academia')
                break

        driver.save_screenshot(f"screenshot2_{state_code}.png")

        print('click NID Interactive Report')
        link = driver.find_element_by_link_text('NID Interactive Report')
        link.click()
        driver.save_screenshot(f"screenshot3_{state_code}.png")

        print('click search')
        search_link = driver.find_element_by_id('apexir_SEARCHDROPROOT')
        search_link.click()
        time.sleep(1)
        driver.save_screenshot(f"screenshot4_{state_code}.png")

        el = driver.find_element_by_id('apexir_columnsearch')
        el.find_element_by_id('STATE').click()
        print('click STATE')
        time.sleep(1)
        driver.save_screenshot(f"screenshot5_{state_code}.png")

        print(f'type {state_code}')
        input_box = driver.find_element_by_id('apexir_SEARCH')
        input_box.clear()
        input_box.send_keys(state_code)
        driver.save_screenshot(f"screenshot6_{state_code}.png")
        print('search')
        driver.execute_script("javascript:gReport.search('SEARCH',100000)")
        print('executed 100000 search')
        time.sleep(5)
        driver.save_screenshot(f"screenshot7_{state_code}.png")
        print("loading table via xpath")
        table_element = driver.find_element_by_xpath(
            "//table[@class='apexir_WORKSHEET_DATA']")
        print("loaded table doc from a string")
        with open(TABLE_PATH, 'a') as table_file:
            for row_index, table_row in enumerate(
                    table_element.find_elements_by_xpath(".//tr")):
                if not wrote_header:
                    for col in table_row.find_elements_by_xpath(".//th"):
                        table_file.write(f'{col.text},')
                    table_file.write('\n')
                    wrote_header = True

                if row_index % 100 == 0:
                    print(f'{state_code}, {row_index}')
                for col in table_row.find_elements_by_xpath(".//td"):
                    table_file.write(f'{col.text},')
                table_file.write('\n')


if __name__ == '__main__':
    main()
