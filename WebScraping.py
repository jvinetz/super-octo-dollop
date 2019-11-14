from selenium.webdriver import Chrome
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup


def main():
    url = "https://www.waytostay.com/"
    soup = get_info(url)
    #print(soup.prettify()) #prints the 'inspect' of the hole page

    # csv_file = open('TripAdvisor.csv', 'w')
    # csv_writer = csv.writer(csv_file)
    # csv_writer.writerow(['Price', 'Contact info'])

    # find place page
    page = soup.find('div', class_="destination-info").a
    raw_data = str(page)
    page = re.search('href=(.*)/', raw_data).group()
    web_page = "https://www.waytostay.com" + page[6:]
    print(web_page)

    # new_source = requests.get(web_page)
    # new_source = new_source.text
    # new_soup = BeautifulSoup(driver.page_source, 'lxml')
    # element = new_soup.find('div', class_="large-6 columns")
    # print(element)


#     csv_writer.writerow([prices[i], phones[i]])
# csv_file.close()

def get_info(url):
    webdriver = r"drive\chromedriver"
    driver = Chrome(webdriver)
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup

def test():
    assert (lambda x: x + 1)(1) == 2


if __name__ == '__main__':
    test()
    main()