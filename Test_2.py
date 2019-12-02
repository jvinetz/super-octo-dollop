#SELENIUM
import re
import requests
from bs4 import BeautifulSoup

source = requests.get(
    'https://www.tripadvisor.com/VacationRentals-g274887-Reviews-Budapest_Central_Hungary-Vacation_Rentals.html')
print(source.status_code)  # 200 means the page was downloaded successfully
source = source.content

soup = BeautifulSoup(source, 'html.parser')
#print(soup.prettify()) #prints the 'inspect' of the hole page

# csv_file = open('TripAdvisor.csv', 'w')
# csv_writer = csv.writer(csv_file)
# csv_writer.writerow(['Price', 'Contact info'])

# find all the property pages
pages = []
for elem in soup.find_all('div', class_="property_title"):
    element = elem.a
    raw_data = str(element)
    try:
        page = re.search('href=(.*)html', raw_data).group()
        web_page = "https://www.tripadvisor.com" + page[6:]
        pages.append(web_page)
    except AttributeError:
        pass
print(pages)

page = pages[0]
new_source = requests.get(page)
new_source = new_source.content
new_soup = BeautifulSoup(source, 'html.parser')
#print(new_soup.prettify())
element = new_soup.find_all('div', class_="vr-overview-Overview__propertyInfoLabel--ynL4L")
print(element)

# prices = []
# for element in soup.find_all('div', class_="_3e12V"):
#     price = element.text
#     prices.append(price)
#
# phones = []
# for element in soup.find_all('div', class_="_35UBu"):
#     phone = element.text
#     phones.append(phone)
#
# for i in range(len(prices)):
#     csv_writer.writerow([prices[i], phones[i]])
#     print(prices[i], phones[i])
#
# csv_file.close()

try:
    max_pages = city_soup.find_all('a', class_="page")[-1]
    print('max pages', max_pages)
except AttributeError:
    max_pages = 2
    print('max pages', max_pages)