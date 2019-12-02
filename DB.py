import sqlite3
import os
import sys
import random
import enums
import pandas as pd

DB_FILENAME = 'WTS.db'
df = pd.DataFrame()
print(type(df))


def create_DB():
    if os.path.exists(DB_FILENAME):
        os.remove(DB_FILENAME)

    with sqlite3.connect(DB_FILENAME) as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE currency (
                            id INT PRIMARY KEY, 
                            name VARCHAR(50)
                            )''')

        cur.execute('''CREATE TABLE place (
                            home_id INT PRIMARY KEY, 
                            city VARCHAR(100),
                            page_link VARCHAR(1000),
                            sleeps INT,
                            area_sqm INT,
                            bedrooms INT, 
                            bathroom INT,
                            price INT,
                            curency_ID,
                            FOREIGN KEY (curency_ID) REFERENCES currency (id))''')
        con.commit()
        cur.close()


def first_fill(data: pd.core.frame.DataFrame):
    '''fill the data'''
    with sqlite3.connect(DB_FILENAME) as con:
        cur = con.cursor()

        index_curr = 0
        curr = {}
        for i in data['curency'].unique():
            cur.execute('''INSERT INTO currency (
                                id , 
                                name 
                        ) VALUES (?, ?)''',
                        [index_curr, i])
            curr[i] = index_curr
            index_curr += 1

        index_trip = 0
        for row in data.head().iterrows():
            cur.execute('''INSERT INTO place (
                            home_id,
                            city ,
                            page_link ,
                            sleeps ,
                            area_sqm ,
                            bedrooms , 
                            bathroom ,
                            price ,
                            curency_ID,
                        ) VALUES (?, ?,?,?,?, ?, ?, ?)''',
                        [index_trip, row['city'], row['page_link'], row['sleeps'], row['area_sqm'],
                         row['bedrooms'], row['bathroom'], row['price'], curr[row['curency']]])
            index_trip += 1

            if index_trip % 10000 == 0:
                con.commit()
    con.commit()
    cur.close()


def update_city(city):
    return None


def update_global():
    return None


def search_price(p_min=0, p_max=sys.maxsize):
    return None


def search_city(city):
    return None


def search_sleeps(s_min=0, s_max=sys.maxsize):
    return None


def search_area(a_min=0, a_max=sys.maxsize):
    return None


def search_bedroom(b_min=0, b_max=sys.maxsize):
    return None


def search_bathroom(b_min=0, b_max=sys.maxsize):
    return None
