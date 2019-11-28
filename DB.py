import sqlite3
import os
import sys
import random

DB_FILENAME = 'WTS.db'


def create_DB():
    if os.path.exists(DB_FILENAME):
        os.remove(DB_FILENAME)

    with sqlite3.connect(DB_FILENAME) as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE house (
                            trip_id INT PRIMARY KEY, 
                            taxi_id INT,
                            city VARCHAR(100),
                            page_link VARCHAR(1000),
                            sleeps INT,
                            area_sqm INT,
                            bedrooms INT, 
                            bathroom INT,
                            price INT,
                            curency_ID
                            FOREIGN KEY (curency_ID) REFERENCES trips (trip_id))''')
        con.commit()
        cur.close()


def update_city(city):
    return None


def update_global():
    return None


def search_price(p_min=0, p_max=sys.maxint):
    return None


def search_city(city):
    return None


def search_sleeps(s_min=0, s_max=sys.maxint):
    return None


def search_area(a_min=0, a_max=sys.maxint):
    return None


def search_bedroom(b_min=0, b_max=sys.maxint):
    return None


def search_bathroom(b_min=0, b_max=sys.maxint):
    return None
