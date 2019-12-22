"""WayToStay Scrapping By Julian Vinetz & Maikel Sitbon
GitHub: https://github.com/jvinetz/super-octo-dollop.git"""
import os

from selenium.webdriver import Chrome
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from DB import *
from selenium.webdriver.chrome.options import Options
from log import Logger
from driver_class import Driver
from scraper_class import Scraper


URL = "https://www.waytostay.com/"
CSV = r'csv/data.csv'
log = Logger()
driver = Driver()
scraper = Scraper()
