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

    # csv_file = open('TripAdvisor.csv', 'w')
    # csv_writer = csv.writer(csv_file)
    # csv_writer.writerow(['Price', 'Contact info'])

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
        city_page = city_soup.find_all('div', class_="tile")
        for city in city_page:
            price = re.search(r'(>)([€£]\w*\s[0-9]*)<', str(city)).group(2)
            print(price)
            detail = city.p.text
            print(str(detail.split()))
        driver.close()


    # new_source = requests.get(web_page)
    # new_source = new_source.text
    # new_soup = BeautifulSoup(driver.page_source, 'lxml')
    # element = new_soup.find('div', class_="large-6 columns")
    # print(element)


#     csv_writer.writerow([prices[i], phones[i]])
# csv_file.close()

def set_driver():
    webdriver = r"drive/chromedriver"
    driver = Chrome(webdriver)
    return driver


def get_info(url, driver):
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def test():
    assert (lambda x: x + 1)(1) == 2


if __name__ == '__main__':
    test()
    main()
