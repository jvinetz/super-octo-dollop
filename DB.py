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


def first_fill(data: list):
    '''fill the data'''

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
                        curency_ID ) VALUES (%s, %s,%s,%s,%s, %s, %s, %s)'''
    index_curr = 0
    curr = {}
    for i in data['curency'].unique():
        my_cursor.execute(currency_form,
                          (index_curr, i))
        curr[i] = index_curr
        index_curr += 1

    index_trip = 0
    for row in data.head().iterrows():
        elmt = (index_trip, row['city'], row['page_link'], row['sleeps'], row['area_sqm'], row['bedrooms'],
                row['bathroom'], row['price'], curr[row['curency']])
        my_cursor.execute(place_form, elmt)
        index_trip += 1
        if index_trip % 10000 == 0:
            my_db.commit()
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
