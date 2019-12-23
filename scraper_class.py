import re
import pandas as pd
from log import Logger
from driver_class import Driver

URL = "https://www.waytostay.com/"
CSV = r'csv/data.csv'


class Scraper:
    def __init__(self):
        """Initialize scraper"""
        self.driver = Driver()
        self.log = Logger()

    def global_update(self):
        """Updates the entire database"""
        url = URL
        soup = self.driver.get_info(url)
        page_list = self.collect_pages(soup)
        arr = []
        for pl in page_list:
            self.scrap(pl, arr)
        df = pd.DataFrame(arr)
        df.to_csv(CSV)
        self.driver.close()
        self.driver.quit()
        return df

    def scrap(self, pl, arr):
        """Scraps evert page and returns the information in a list of dictionaries"""
        city_soup = self.driver.get_info(pl)
        num_pages = self.find_num_pages(city_soup, self.log)
        for i in range(num_pages):
            city_page = city_soup.find_all('div', class_="tile")
            for city in city_page:
                try:
                    price = re.search(r'(>)([€£]\w*\s[0-9]*)<', str(city)).group(2)
                except AttributeError:
                    self.log.error('"scrap" raised an ValueError on num_pages')
                    price = '€ 0'
                page_link = city.a['href']
                detail = city.p.text.split()
                if detail[1] == 'sqm':
                    detail = [detail[0]] + ['0', '0'] + detail[1:]
                dic = {"city": pl, "page_link": page_link, 'sleeps': detail[1], 'area_sqm': detail[2],
                       'bedrooms': detail[4], 'bathroom': detail[6], 'price': price[2:], 'currency': price[0]}
                arr.append(dic)
            if num_pages != 1:
                city_soup = self.driver.next_page(i, pl)
        return arr

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def find_num_pages(city_soup, log):
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
