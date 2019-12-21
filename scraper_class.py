import re
from WebScraping import URL

class Scraper:
    def __init__(self, driver):
        """Initialize scraper"""
        self.driver = driver

    def scrap(self, pl, arr, driver):
        """Scraps evert page and returns the information in a list of dictionaries"""
        city_soup = driver.get_info(pl)
        num_pages = self.find_num_pages(city_soup)
        for i in range(num_pages):
            city_page = city_soup.find_all('div', class_="tile")
            for city in city_page:
                try:
                    price = re.search(r'(>)([€£]\w*\s[0-9]*)<', str(city)).group(2)
                except AttributeError:
                    log.error('"scrap" raised an ValueError on num_pages')
                    price = '€ 0'
                page_link = city.a['href']
                detail = city.p.text.split()
                dic = {"city": pl, "page_link": page_link, 'sleeps': detail[1], 'area_sqm': detail[2],
                       'bedrooms': detail[4], 'bathroom': detail[6], 'price': price[2:], 'currency_ID': price[0]}
                arr.append(dic)
            if num_pages != 1:
                city_soup = driver.next_page(i, pl)
        driver.close()
        return arr


    def collect_pages(self, soup):
        """Gets the the page of each city and returns all of them in a list"""
        page = soup.find_all('div', class_="destination-info")
        page_list = []
        for p in page:
            raw_data = str(p)
            page = re.search('href=(.*)/', raw_data).group()
            web_page = URL[:-1] + page[6:]
            page_list.append(web_page)
        return page_list

    def find_num_pages(self, city_soup, log):
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
