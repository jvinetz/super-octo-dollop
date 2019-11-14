from selenium.webdriver import Chrome
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

webdriver = r"C:\Users\jvine\Downloads\chromedriver_win32\chromedriver.exe"
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












#SACADO DE UN TUTORIAL
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