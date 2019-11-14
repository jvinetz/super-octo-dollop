#FALTA AGREGAR LO DE SELENIUM

import re
import requests
from bs4 import BeautifulSoup


def main():
    source = requests.get('https://www.waytostay.com/')
    print(source.status_code)  # 200 means the page was downloaded successfully
    #source = source.text

    soup = BeautifulSoup(source, 'lxml')
    print(soup.prettify()) #prints the 'inspect' of the hole page

    # csv_file = open('TripAdvisor.csv', 'w')
    # csv_writer = csv.writer(csv_file)
    # csv_writer.writerow(['Price', 'Contact info'])

    # find place page
    page = soup.find('div', class_="destination-info").a
    raw_data = str(page)
    page = re.search('href=(.*)/', raw_data).group()
    web_page = "https://www.waytostay.com" + page[6:]
    print(web_page)

    new_source = requests.get(web_page)
    new_source = new_source.text
    new_soup = BeautifulSoup(source, 'lxml')
    element = new_soup.find('div', class_="large-6 columns")
    print(element)


#     csv_writer.writerow([prices[i], phones[i]])
# csv_file.close()




def test():
    assert (lambda x: x + 1)(1) == 2


if __name__ == '__main__':
    test()
    main()