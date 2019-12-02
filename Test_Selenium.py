from selenium.webdriver import Chrome
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import os


def main():
    webdriver = os.path.join(r"drive","chromedriver" )
    driver = Chrome(webdriver)

    url = "https://www.waytostay.com/paris-apartments/"
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    info = driver.find_elements_by_class_name("tile")
    prices = []
    details = []
    for j in range(len(info)):
        prices.append(driver.find_elements_by_class_name('price-person')[j].text)
        details.append(driver.find_elements_by_class_name('concise-details')[j].text)
    print(prices, details)
    driver.close()
    driver.quit()


def test():
    assert (lambda x: x + 1)(1) == 2


if __name__ == '__main__':
    test()
    main()

# SACADO DE UN TUTORIAL
# total = []
# for item in range(items):
#     quotes = driver.find_elements_by_class_name("quote")
#     for quote in quotes:
#         quote_text = quote.find_element_by_class_name('text').text
#         author = quote.find_element_by_class_name('author').text
#         new = ((quote_text,author))
#         total.append(new)
# df = pd.DataFrame(total,columns=['quote','author'])
# df.to_csv('quoted.csv')
