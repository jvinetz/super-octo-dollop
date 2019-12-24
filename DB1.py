import re

import DB
import pandas as pd

db = DB.DB(host="localhost", user="root", passwd='ITCITCITC', use_pure=True, database='Scraper', buffered=True)
# db.create_tables()
# a = db.fill_cheapest_trip('TLV', date_departure='2020-03-01', date_return='2020-04-01', peoples=3, currency='ILS', sleeps=2,cheap=True)
# print(a)
# data = pd.read_csv(r'csv/data1.csv')
# data = data.iloc[:, 1:]

# db.first_fill(data)
# db.update_city('miami',data)
db.add_lon_lat_to_db()
