import re
import time

import mysql.connector
import pandas as pd
from API import Fly_API

my_db = mysql.connector.connect(
    host="localhost",
    user="ITC",
    passwd='ITCITCITC',
    use_pure=True,
    database='Scraper'
)

my_cursor = my_db.cursor(buffered=True)


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
                            currency_ID INTEGER(10),
                            FOREIGN KEY (currency_ID) REFERENCES currency (id))''')

    my_cursor.execute('''CREATE TABLE airports (
                                    city VARCHAR(255) PRIMARY KEY, 
                                    airport_id VARCHAR(255)
                                    )''')


def first_fill(data: pd.core.frame.DataFrame):
    """fill the data"""

    data, data_prep_list, curr_list = prep_data(data)

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
                        currency_ID ) VALUES (%s, %s,%s,%s,%s, %s, %s, %s, %s)'''

    # execution :
    my_cursor.executemany(currency_form, curr_list)
    my_cursor.executemany(place_form, data_prep_list)

    my_db.commit()

    insert_airports()


def update_city(city, df_new):
    # Delete apartments that are no longer in the page
    df_new['page_link'].drop_duplicates(inplace=True)
    df_old = get_old_df(city)

    new_apartments = (str(list(df_new['page_link'].values))).strip('[]')
    remove_obsolete_apt(df_old, new_apartments)

    num_col = df_new.columns
    insert_new_apt(df_new, df_old, num_col)
    if not df_old.empty:
        update_old_apt(df_old, df_new, num_col)


def get_old_df(city):
    """Gets old data from DB"""
    try:
        df_old = get_query_df('SELECT * FROM place WHERE city = "https://www.waytostay.com/' + city + '-apartments/"')
    except mysql.connector.errors.InternalError:
        df_old = pd.DataFrame()
        print('Inserting new city')
    df_old['page_link'].drop_duplicates(inplace=True)
    return df_old


def insert_new_apt(df_new, df_old):
    """Insert new apartments into DB"""
    if not df_old.empty:
        df_insert = df_new.merge(df_old, on='page_link', how='left', indicator=True).query(
            '_merge == "left_only"').drop('_merge', 1)
        df_insert = df_insert[df_insert.columns[0:len(df_new.columns)]]
        df_insert.columns = num_col
    else:
        df_insert = df_new
    data, data_prep_list, curr_list = prep_data(df_insert)
    try:
        my_cursor.execute("SELECT MAX(home_id) FROM place")
        max_id = my_cursor.fetchall()
        for i in range(max_id[0][0] + 1, max_id[0][0] + 1 + len(data_prep_list)):
            data_prep_list[i - max_id[0][0] - 1].insert(0, i)
    except TypeError:
        for i in range(len(data_prep_list)):
            data_prep_list[i].insert(0, i)

    except mysql.connector.errors.InternalError:
        for i in range(len(data_prep_list)):
            data_prep_list[i].insert(0, i)
    query_2 = """INSERT INTO place (
                                    home_id,
                                    city ,
                                    page_link ,
                                    sleeps ,
                                    area_sqm ,
                                    bedrooms , 
                                    bathroom ,
                                    price ,
                                    currency_ID ) VALUES (%s, %s,%s,%s,%s, %s, %s, %s, %s)"""
    my_cursor.executemany(query_2, data_prep_list)
    my_db.commit()


def update_old_apt(df_new, df_old, num_col):
    """Update apartments whose data has been changed"""

    df_update = df_new.merge(df_old, on='page_link', how='inner', indicator=True)
    df_update = df_update[df_update.columns[0:len(df_new.columns)]]
    df_update.columns = num_col

    upd_apartments = (str(list(df_update['page_link'].values))).strip('[]')
    query_3 = "DELETE FROM place WHERE page_link NOT IN ({0})".format(upd_apartments)
    my_cursor.execute(query_3)
    data, data_prep_list, curr_list = prep_data(df_update)
    my_cursor.execute("SELECT MAX(home_id) FROM place")
    max_id = my_cursor.fetchall()
    time.sleep(2)
    for i in range(max_id[0][0] + 1, max_id[0][0] + 1 + len(data_prep_list)):
        data_prep_list[i - max_id[0][0] - 1] = data_prep_list[i - max_id[0][0] - 1].insert(0, i)

    time.sleep(2)
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


def remove_obsolete_apt(df_old, new_apartments):
    if not df_old.empty:
        query_1 = "DELETE FROM place WHERE page_link NOT IN ({0})".format(new_apartments)
        my_cursor.execute(query_1)


def update_global(df_new):
    try:
        my_cursor.execute("SELECT MAX(home_id) FROM place")
    except mysql.connector.errors.InternalError:
        create_db()
        create_tables()
    finally:
        for city in df_new['city'].unique():
            city_name = re.search(r'https://www.waytostay.com/([a-z]*)-apartments/', str(city)).group(1)
            update_city(city_name, df_new[df_new['city'] == city])
        airports(df_new['city'])


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


def insert_airports():
    """Inserts data to the airport table"""

    airports_form = '''INSERT INTO airports (city ,airport_id ) VALUES (%s, %s)'''
    df = get_query_df('SELECT city FROM place')
    df.columns = ['city']
    df['airport'] = ''

    api = Fly_API.Fly
    for i in range(len(df)):
        df['airport'].iloc[i] = api.find_airport_by_city_name(df.iloc[i]['city'])

    my_cursor.executemany(airports_form, df.values.tolist())
    my_db.commit()


def update_airport(result, df_city):
    """Updates the airports table if already exists"""
    new_airs = result[result != df_city]
    new_airs['airport'] = ''

    api = Fly_API.Fly
    for i in range(len(new_airs)):
        new_airs['airport'].iloc[i] = api.find_airport_by_city_name(new_airs.iloc[i]['city'])

    airports_form = '''INSERT INTO airports (city ,airport_id ) VALUES (%s, %s)'''
    my_cursor.executemany(airports_form, new_airs.values.tolist())
    my_db.commit()


def airports(df_city):
    my_cursor.execute("SELECT * FROM airports")
    result = my_cursor.fetchall()

    if not result:
        insert_airports()

    else:
        update_airport(result, df_city)
