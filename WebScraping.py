"""WayToStay Scrapping By Julian Vinetz & Maikel Sitbon """

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

    arr = []
    #index = 0
    for pl in page_list:
        driver = set_driver()
        city_soup = get_info(pl, driver)
        try:
            max_pages = city_soup.find('a', class_="last")
        except AttributeError:
            max_pages = city_soup.find_all('a', class_="page")[-1]
        try:
            num_pages = int(max_pages.text) - 1
        except AttributeError:
            num_pages = 1
        except ValueError:
            num_pages = 0
        for i in range(num_pages):
            city_page = city_soup.find_all('div', class_="tile")
            for city in city_page:
                price = re.search(r'(>)([€£]\w*\s[0-9]*)<', str(city)).group(2)
                page_link = city.a['href']
                detail = city.p.text.split()
                dic = {"city": pl, "page_link": page_link, 'sleeps': detail[1], 'area_sqm': detail[2],
                       'bedrooms': detail[4], 'bathroom': detail[6], 'price': price[2:], 'curency': price[0]}
                arr.append(dic)
            if num_pages != 1:
                city_soup = next_page(driver, i, pl)
            print(arr)
        driver.close()
        #index += 1
        #if index == 4:
        #   break
    # df = pd.DataFrame(columns=['link', 'sleeps', 'area_sqm', 'bedrooms', 'bathroom', 'city', 'price'])
    df = pd.DataFrame(arr)
    df.to_csv(r'csv/data.csv')
    print(df.head())
    driver.quit()
    # new_source = requests.get(web_page)
    # new_source = new_source.text
    # new_soup = BeautifulSoup(driver.page_source, 'lxml')
    # element = new_soup.find('div', class_="large-6 columns")
    # print(element)


#     csv_writer.writerow([prices[i], phones[i]])
# csv_file.close()

def set_driver():
    """Set-up the driver"""
    webdriver = r"drive/chromedriver"
    driver = Chrome(webdriver)
    return driver


def get_info(url, driver):
    """Set up Beautiful Soup"""
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def next_page(driver, i, pl):
    """Allow to navigate between pages"""
    url = pl + '#page=' + str(i + 2) + '&perPage=12'
    city_soup = get_info(url, driver)
    return city_soup


def test():
    assert (lambda x: x + 1)(1) == 2


if __name__ == '__main__':
    test()
    main()
