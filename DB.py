import sys
import time
import re

import mysql.connector
import pandas as pd

my_db = mysql.connector.connect(
    host="localhost",
    user="ITC",
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

    data, data_prep_list, curr_list = prep_data(data)

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


def update_city(city, df_new):
    # Delete apartments that are no longer in the page
    df_old = get_query_df('SELECT * FROM place WHERE city = "https://www.waytostay.com/' + city + '-apartments/"')
    new_apartments = (str(list(df_new['page_link'].values))).strip('[]')
    query_1 = "DELETE FROM place WHERE page_link NOT IN ({0})".format(new_apartments)
    my_cursor.execute(query_1)

    # Insert new apartments
    num_col = df_new.columns
    df_insert = df_new.merge(df_old, on='page_link', how='left', indicator=True).query('_merge == "left_only"').drop('_merge', 1)
    df_insert = df_insert[df_insert.columns[0:len(df_new.columns)]]
    df_insert.columns = num_col
    data, data_prep_list, curr_list = prep_data(df_insert)
    my_cursor.execute("SELECT MAX(home_id) FROM place")
    max_id = my_cursor.fetchall()
    for i in range(max_id[0][0] + 1, max_id[0][0] + 1 + len(data_prep_list)):
        data_prep_list[i-max_id[0][0] - 1].insert(0, i)
    query_2 = """INSERT INTO place (
                                home_id,
                                city ,
                                page_link ,
                                sleeps ,
                                area_sqm ,
                                bedrooms , 
                                bathroom ,
                                price ,
                                curency_ID ) VALUES (%s, %s,%s,%s,%s, %s, %s, %s, %s)"""
    my_cursor.executemany(query_2, data_prep_list)

    # Update apartments whose data has been changed

    df_update = df_new.merge(df_old, on='page_link', how='inner', indicator=True)
    df_update = df_update[df_update.columns[0:len(df_new.columns)]]
    df_update.columns = num_col

    upd_apartments = (str(list(df_update['page_link'].values))).strip('[]')
    query_3 = "DELETE FROM place WHERE page_link NOT IN ({0})".format(upd_apartments)
    my_cursor.execute(query_3)

    data, data_prep_list, curr_list = prep_data(df_update)
    my_cursor.execute("SELECT MAX(home_id) FROM place")
    max_id = my_cursor.fetchall()
    for i in range(max_id[0][0] + 1, max_id[0][0] + 1 + len(data_prep_list)):
        data_prep_list[i - max_id[0][0] - 1].insert(0, i)
    query_4 = """INSERT INTO place (
                                    home_id,
                                    city ,
                                    page_link ,
                                    sleeps ,
                                    area_sqm ,
                                    bedrooms , 
                                    bathroom ,
                                    price ,
                                    curency_ID ) VALUES (%s, %s,%s,%s,%s, %s, %s, %s, %s)"""
    my_cursor.executemany(query_4, data_prep_list)
    my_db.commit()


def update_global(df_new):
    try:
        create_db()
        create_tables()
    finally:
        for city in df_new['city'].unique():
            city_name = re.search(r'https://www.waytostay.com/([a-z]*)-apartments/', str(city)).group(1)
            print(city_name)
            update_city(city_name, df_new[df_new['city'] == city])


def get_query_df(query):
    df = pd.read_sql_query(query, my_db)
    return df


def prep_data(data):
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
    return data, data_prep_list, curr_list


def get_query_df(query):
    df = pd.read_sql(query, my_db)
    return df