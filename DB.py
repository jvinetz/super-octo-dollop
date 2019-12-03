import os
import sys
import random
import enums
import pandas as pd
import mysql.connector

my_db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd='ITCITCITC',
    use_pure=True,
    database='Scraper'
)

my_cursor = my_db.cursor()


def create_db():
    try:
        my_cursor.execute(" CREATE DATABASE Scraper ")
    except mysql.connector.errors.DatabaseError:
        print('database already exist')


def create_tables():
    my_cursor.execute('''CREATE TABLE currency (
                            id INTEGER(10) PRIMARY KEY, 
                            name VARCHAR(255)
                            )''')

    my_cursor.execute('''CREATE TABLE place (
                            home_id INTEGER(10) PRIMARY KEY, 
                            city VARCHAR(100),
                            page_link VARCHAR(1000),
                            sleeps INTEGER(10),
                            area_sqm INTEGER(10),
                            bedrooms INTEGER(10), 
                            bathroom INTEGER(10),
                            price INTEGER(10),
                            curency_ID INTEGER(10),
                            FOREIGN KEY (curency_ID) REFERENCES currency (id))''')


def first_fill(data: pd.core.frame.DataFrame):
    """fill the data"""
# prepare the data:
    data = data.fillna(-1)
    # currency:
    curr_unique = data['curency'].unique().tolist()
    curr_list = [[i, curr_unique[i]] for i in range(len(curr_unique))]
    curr = {i[1]: i[0] for i in curr_list}

    # other :
    data['curency'] = data['curency'].apply(lambda x: curr[x])
    data['bedrooms'] = data['bedrooms'].apply(lambda x: int(x) if x != 'studio' else 0)
    data_prep_list = data.values.tolist()
    print(data_prep_list)
    for i in range(len(data_prep_list)):
        data_prep_list[i].insert(0, i)

    # SQL request :
    currency_form = '''INSERT INTO currency (id ,name ) VALUES (%s, %s)'''
    place_form = '''INSERT INTO place (
                        home_id,
                        city ,
                        page_link ,
                        sleeps ,
                        area_sqm ,
                        bedrooms , 
                        bathroom ,
                        price ,
                        curency_ID ) VALUES (%s, %s,%s,%s,%s, %s, %s, %s, %s)'''

    # execution :
    my_cursor.executemany(currency_form, curr_list)
    my_cursor.executemany(place_form, data_prep_list)

    my_db.commit()


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
