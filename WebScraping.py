"""WayToStay Scrapping By Julian Vinetz & Maikel Sitbon
GitHub: https://github.com/jvinetz/super-octo-dollop.git"""
import os

from selenium.webdriver import Chrome
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from DB import *

URL = "https://www.waytostay.com/"
CSV = r'csv/data.csv'


def global_update():
    """Updates the entire database"""
    url = URL
    driver = set_driver()
    soup = get_info(url, driver)
    page_list = collect_pages(soup)
    driver.close()

    arr = []
    i=0
    for pl in page_list:
        scrap(pl, arr)
        i += 1
        if i == 1:
            break

    df = pd.DataFrame(arr)
    df.to_csv(CSV)

    driver.quit()
    return df


def scrap(pl, arr):
    """Scraps evert page and returns the information in a list of dictionaries"""
    driver = set_driver()
    city_soup = get_info(pl, driver)
    num_pages = find_num_pages(city_soup)
    for i in range(num_pages):
        city_page = city_soup.find_all('div', class_="tile")
        for city in city_page:
            try:
                price = re.search(r'(>)([€£]\w*\s[0-9]*)<', str(city)).group(2)
            except AttributeError:
                price = '€ 0'
            page_link = city.a['href']
            detail = city.p.text.split()
            dic = {"city": pl, "page_link": page_link, 'sleeps': detail[1], 'area_sqm': detail[2],
                   'bedrooms': detail[4], 'bathroom': detail[6], 'price': price[2:], 'curency': price[0]}
            arr.append(dic)
        if num_pages != 1:
            city_soup = next_page(driver, i, pl)
    driver.close()
    return arr


def collect_pages(soup):
    """Gets the the page of each city and returns all of them in a list"""
    page = soup.find_all('div', class_="destination-info")
    page_list = []
    for p in page:
        raw_data = str(p)
        page = re.search('href=(.*)/', raw_data).group()
        web_page = URL[:-1] + page[6:]
        page_list.append(web_page)
    return page_list


def find_num_pages(city_soup):
    """Finds out the number of pages tha the city has and returns it"""
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
    return num_pages


def set_driver():
    """Set-up the driver"""
    webdriver = os.path.join(r"drive", "chromedriver")
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
