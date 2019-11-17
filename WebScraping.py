from selenium.webdriver import Chrome
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup


def main():
    url = "https://www.waytostay.com/"
    driver = set_driver()
    soup = get_info(url, driver)
    # print(soup.prettify()) #prints the 'inspect' of the hole page

    # find place page
    page = soup.find_all('div', class_="destination-info")
    page_list = []
    for p in page:
        raw_data = str(p)
        page = re.search('href=(.*)/', raw_data).group()
        web_page = "https://www.waytostay.com" + page[6:]
        page_list.append(web_page)
    driver.close()

    apartment_info = {}
    for pl in page_list:
        driver = set_driver()
        city_soup = get_info(pl, driver)
        for i in range(10):
            city_page = city_soup.find_all('div', class_="tile")
            for city in city_page:
                price = re.search(r'(>[$€]\s)([0-9]*)<', str(city)).group(2)
                print(price)
                detail = city.p.text
                print(str(detail.split()))
                apartment_link = city.a['href']
                print(apartment_link)
            city_soup = next_page(driver)
        driver.close()


def set_driver():
    webdriver = r"drive/chromedriver"
    driver = Chrome(webdriver)
    return driver


def get_info(url, driver):
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def next_page(driver):
    next_button = driver.find_element_by_class_name('next')
    next_button.click()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    city_soup = BeautifulSoup(driver.page_source, "html.parser")
    return city_soup


def test():
    assert (lambda x: x + 1)(1) == 2


if __name__ == '__main__':
    test()
    main()
