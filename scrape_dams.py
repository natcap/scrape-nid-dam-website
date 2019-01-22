"""Scrape dam inventory."""
import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select

def main():

    my_url = "http://nid.usace.army.mil/cm_apex/f?p=838:4:0::NO"
    driver = webdriver.PhantomJS()
    driver.get(my_url)

    driver.save_screenshot("screenshot.png")
    el = driver.find_element_by_id('P12_ORGANIZATION')
    for option in el.find_elements_by_tag_name('option'):
        print(option.text)
        if option.text == 'Academia':
            option.click()  # select() in earlier versions of webdriver
            print('clicked academia')
            break

    driver.save_screenshot("screenshot2.png")
    link = driver.find_element_by_link_text('NID Interactive Report')
    link.click()
    driver.save_screenshot("screenshot3.png")

    search_link = driver.find_element_by_id('apexir_SEARCHDROPROOT')
    search_link.click()
    time.sleep(5)
    driver.save_screenshot("screenshot4.png")

    el = driver.find_element_by_id('apexir_columnsearch')
    el.find_element_by_id('STATE').click()
    time.sleep(5)
    driver.save_screenshot("screenshot5.png")

    input_box = driver.find_element_by_id('apexir_SEARCH')
    input_box.clear()
    input_box.send_keys('AZ')
    driver.save_screenshot("screenshot6.png")
    driver.execute_script("javascript:gReport.search('SEARCH',100000)")
    time.sleep(5)
    driver.save_screenshot("screenshot7.png")


    #table = driver.find_element_by_class_name('apexir_WORKSHEET_DATA')
    #print(table)

    #apex.submit(&#x27;P12_ORGANIZATION&#x27;)
    #p_element = driver.find_element_by_id(id_='intro-text')
    #print(p_element.text)


if __name__ == '__main__':
    main()
