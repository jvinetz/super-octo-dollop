import argparse
import re
import sys

import pandas as pd
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from selenium.webdriver import Chrome

import DB
import WebScraping
from log import Logger

URL = "https://www.waytostay.com/en"
CSV = r'csv/data.csv'
con = DB.my_db
log = Logger()


def update_db(user_city):
    """Updates the database with the information the user placed as input"""
    url = URL
    driver = set_driver()
    soup = get_info(url, driver)
    web_page = find_city(soup, user_city)
    driver.close()

    driver = set_driver()
    city_soup = get_info(web_page, driver)
    num_pages = find_num_pages(city_soup)

    df = create_table(num_pages, web_page, driver, city_soup)
    df['sleeps'].apply(lambda x: int(x))
    df['area_sqm'].apply(lambda x: int(x))
    df['bedrooms'].apply(lambda x: int(x) if x != 'studio' else 0)
    df['bathroom'].apply(lambda x: int(x))
    df['price'].apply(lambda x: int(x))

    DB.update_city(user_city, df)

    driver.close()
    driver.quit()

    return df


def create_table(num_pages, web_page, driver, city_soup):
    """Scraps the input page and returns a dataframe with the information"""
    arr = []
    for i in range(num_pages):
        city_page = city_soup.find_all('div', class_="tile")
        for city in city_page:
            price = re.search(r'(>)([€£]\w*\s[0-9]*)<', str(city)).group(2)
            page_link = city.a['href']
            detail = city.p.text.split()
            dic = {"city": web_page, "page_link": page_link, 'sleeps': detail[1], 'area_sqm': detail[2],
                   'bedrooms': detail[4], 'bathroom': detail[6], 'price': price[2:], 'currency_ID': price[0]}
            arr.append(dic)
        if num_pages != 1:
            city_soup = next_page(driver, i, web_page)
    df = pd.DataFrame(arr)
    return df


def find_num_pages(city_soup):
    """Finds out the number of pages tha the city has and returns it"""
    try:
        max_pages = city_soup.find('a', class_="last")
    except AttributeError:
        log.error('"find_num_pages" raised an AttributeError on max_pages')
        max_pages = city_soup.find_all('a', class_="page")[-1]
    try:
        num_pages = int(max_pages.text) - 1
    except AttributeError:
        log.error('"find_num_pages" raised an AttributeError on num_pages')
        num_pages = 1
    except ValueError:
        log.error('"find_num_pages" raised an ValueError on num_pages')
        num_pages = 0
    return num_pages


def find_city(soup, user_city):
    """Find the wanted city page"""
    page = soup.find_all('div', class_="destination-info")
    web_page = ""
    for p in page:
        raw_data = str(p)
        page = re.search('href=(.*)/', raw_data).group()
        if page[6:] == '/' + user_city + "-apartments/":
            web_page = "https://www.waytostay.com/en" + page[6:]
    return web_page


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


def get_results(args, df):
    """Filters the dataframe with the ranges selected by the user"""

    if args.p:
        if args.argp2:
            df = df[df['price'] < args.argp2]
        df = df[df['price'] > args.argp1]

    if args.s:
        if args.args2:
            df = df[df['sleeps'] < args.args2]
        df = df[df['sleeps'] > args.args1]

    if args.a:
        if args.arga2:
            df = df[df['area_sqm'] < args.arga2]
        df = df[df['area_sqm'] > args.arga1]

    if args.be:
        if args.argbe2:
            df = df[df['bedrooms'] < args.argbe2]
        df = df[df['bedrooms'] > args.argbe1]

    if args.ba:
        if args.argba2:
            df = df[df['bathroom'] < args.argba2]
        df = df[df['bathroom'] > args.argba1]

    return df


def parser():
    """The function calls the scraper to scrap and shows results according to the parameters the user selected as
    inputs """
    parser = argparse.ArgumentParser(
        description='Must insert argument -G for global update or --city "city_name" for city update. '
                    'Then insert the rest of the arguments if wanted')
    parser.add_argument('-G', action="store_true", help='Global update')
    parser.add_argument('--city', help='city')
    parser.add_argument('-p', action="store_true", help='price')
    parser.add_argument('--argp1', nargs='?', default=0, type=int, help='price lower limit')
    parser.add_argument('--argp2', nargs='?', type=int, help='price higher limit')
    parser.add_argument('-s', action="store_true", help='sleeps')
    parser.add_argument('--args1', nargs='?', default=0, type=int, help='sleeps lower limit')
    parser.add_argument('--args2', nargs='?', type=int, help='sleeps higher limit')
    parser.add_argument('-a', action="store_true", help='area')
    parser.add_argument('--arga1', nargs='?', default=0, type=int, help='area lower limit')
    parser.add_argument('--arga2', nargs='?', type=int, help='area higher limit')
    parser.add_argument('-be', action="store_true", help='bedrooms')
    parser.add_argument('--argbe1', nargs='?', default=0, type=int, help='bedrooms lower limit')
    parser.add_argument('--argbe2', nargs='?', type=int, help='bedrooms higher limit')
    parser.add_argument('-ba', action="store_true", help='bathrooms')
    parser.add_argument('--argba1', nargs='?', default=0, type=int, help='bathrooms lower limit')
    parser.add_argument('--argba2', nargs='?', type=int, help='bathrooms higher limit')
    parser.add_argument('--curr', action="store_true", help='currency')
    args = parser.parse_args()
    return args, parser


def get_coords(city):
    """The function gets the latitud and longitud for the input city"""
    geolocator = Nominatim(user_agent="ITC_DM")
    location = geolocator.geocode(city, timeout=5)
    latitude = location.latitude
    longitude = location.longitude
    return latitude, longitude


def main():
    args, par = parser()
    if args.city:
        update_db(args.city)
        df = DB.get_query_df("""SELECT * FROM place""")
        results = get_results(args, df)
        print("The city has been updated/created in the database")
        print(results)
    elif args.G:
        df = WebScraping.global_update()
        DB.update_global(df)
        print(df)
        print("The database has been created/updated")
    else:
        print(
            "\nThere were not enough parameters to scrap, please be sure to input at least the '-G' or '--city' "
            "parameters\n")
        par.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
