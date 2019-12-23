from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

URL = "https://www.waytostay.com/en"


class Driver:
    def __init__(self):
        """Initialize chrome driver"""

        self.webdriver = r"./chromedriver"
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = Chrome(self.webdriver, chrome_options=self.chrome_options)

    def get_info(self, url):
        """Set up Beautiful Soup"""
        self.driver.get(url)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        return soup

    def next_page(self, i, pl):
        """Allow to navigate between pages"""
        url = pl + '#page=' + str(i + 2) + '&perPage=12'
        city_soup = self.get_info(url)
        return city_soup

    def close(self):
        """Closes the driver"""
        self.driver.close()

    def quit(self):
        """Quits the driver"""
        self.driver.quit()
