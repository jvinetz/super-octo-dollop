import argparse
import re
from selenium.webdriver import Chrome
import pandas as pd
from bs4 import BeautifulSoup


def update_db(user_city):
    url = "https://www.waytostay.com/"
    driver = set_driver()
    soup = get_info(url, driver)
    web_page = find_city(soup, user_city)
    driver.close()

    arr = []
    driver = set_driver()
    city_soup = get_info(web_page, driver)
    num_pages = find_num_pages(city_soup)

    for i in range(num_pages):
        city_page = city_soup.find_all('div', class_="tile")
        for city in city_page:
            price = re.search(r'(>)([€£]\w*\s[0-9]*)<', str(city)).group(2)
            page_link = city.a['href']
            detail = city.p.text.split()
            dic = {"city": web_page, "page_link": page_link, 'sleeps': detail[1], 'area_sqm': detail[2],
                   'bedrooms': detail[4], 'bathroom': detail[6], 'price': price[2:], 'curency': price[0]}
            arr.append(dic)
        if num_pages != 1:
            city_soup = next_page(driver, i, web_page)
    df = pd.DataFrame(arr)
    df.to_csv(r'csv/data.csv')
    print(df.head())
    driver.close()
    driver.quit()


def find_num_pages(city_soup):
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


def find_city(soup, user_city):
    """Find the wanted city page"""
    page = soup.find_all('div', class_="destination-info")
    for p in page:
        raw_data = str(p)
        page = re.search('href=(.*)/', raw_data).group()
        if page[6:] == '/' + user_city + "-apartments/":
            web_page = "https://www.waytostay.com" + page[6:]
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


def get_results(args):
    df = pd.read_csv(r'csv/data.csv')
    if args.p:
        if args.argp2:
            df = df[df['price'] < args.argp2]
        df = df[df['price'] > args.argp1]
    return df


def parser():
    """The function calls a function from [add, multiply, divide, subtract] depending on the input from the user """
    parser = argparse.ArgumentParser(description='')
    subparsers = parser.add_subparsers(help='different items')

    parser.add_argument("city", type=str, help="City")

    p_parser = subparsers.add_parser("p")
    p_parser.add_argument('-argp1', nargs='?', const=0, type=int, help='lower limit')
    p_parser.add_argument('-argp2', nargs='?', type=int, help='higher limit')

    s_parser = subparsers.add_parser("s")
    s_parser.add_argument('-args1', nargs='?', const=0, type=int, help='lower limit')
    s_parser.add_argument('-args2', nargs='?', type=int, help='higher limit')

    a_parser = subparsers.add_parser("a")
    a_parser.add_argument('-arga1', nargs='?', const=0, type=int, help='lower limit')
    a_parser.add_argument('-arga2', nargs='?', type=int, help='higher limit')

    be_parser = subparsers.add_parser("-be")
    be_parser.add_argument('-argbe1', nargs='?', const=0, type=int, help='lower limit')
    be_parser.add_argument('-argbe2', nargs='?', type=int, help='higher limit')

    ba_parser = subparsers.add_parser("-ba")
    ba_parser.add_argument('-argba1', nargs='?', const=0, type=int, help='lower limit')
    ba_parser.add_argument('-argba2', nargs='?', type=int, help='higher limit')

    pargs = p_parser.parse_args()
    sargs = s_parser.parse_args()
    aargs = a_parser.parse_args()
    beargs = be_parser.parse_args()
    baargs = ba_parser.parse_args()
    args = [pargs, sargs, aargs, beargs, baargs]
    return args


def main():
    args = parser()
    print(args)
    #print(get_results(args))
    #update_db(args.city)
    #print(globals()[get_results](city, pl, ph, sl, sh, al, ah, bel, beh, bal, bah))


if __name__ == "__main__":
    main()