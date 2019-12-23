import re

import mysql.connector
import pandas as pd

import personal_debug
from API.Fly_API import Fly
from log import Logger


class DB:
    def __init__(self, host, user, passwd, use_pure, database, buffered):
        self.my_db = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            use_pure=use_pure,
            database=database
        )

        self.my_cursor = self.my_db.cursor(buffered=buffered)
        self.log = Logger()

    def create_db(self):
        try:
            self.my_cursor.execute(" CREATE DATABASE Scraper ")
        except mysql.connector.errors.DatabaseError:
            print('database already exist')
            self.log.error('database already exist')

    def create_tables(self):
        try:
            self.my_cursor.execute('''CREATE TABLE currency (
                                id INTEGER(10) PRIMARY KEY, 
                                name VARCHAR(255)
                                )''')
        except mysql.connector.errors.DatabaseError:
            print('currency table already exist')
            self.log.error('currency table already exist')

        try:
            self.my_cursor.execute('''CREATE TABLE place (
                                home_id INTEGER(10) PRIMARY KEY, 
                                city VARCHAR(100),
                                page_link VARCHAR(1000),
                                sleeps INTEGER(10),
                                area_sqm INTEGER(10),
                                bedrooms INTEGER(10), 
                                bathroom INTEGER(10),
                                price INTEGER(10),
                                currency_ID INTEGER(10),
                                FOREIGN KEY (currency_ID) REFERENCES currency (id),
                                FOREIGN KEY (city) REFERENCES city (city)
                                )''')
        except mysql.connector.errors.DatabaseError:
            print('place table already exist')
            self.log.error('place table already exist')

        try:
            self.my_cursor.execute('''CREATE TABLE city (
                                        city VARCHAR(255) PRIMARY KEY, 
                                        airport_id VARCHAR(255)
                                        )''')
        except mysql.connector.errors.DatabaseError:
            print('city table already exist')
            self.log.error('city table already exist')

    def first_fill(self, data: pd.core.frame.DataFrame):
        """fill the data"""
        # set-up data
        curr_dic = self.prep_data_currency(data)
        data = self.prep_data(data, curr_dic)
        city_dic = self.prep_data_city(data)

        # set-up lists:
        data_prep_list = data.values.tolist()
        curr_list = [[curr_dic[i], i] for i in curr_dic.keys()]
        city_list = [[i, city_dic[i]] for i in city_dic.keys()]

        for i in range(len(data_prep_list)):
            data_prep_list[i].insert(0, i)

        # SQL request :
        city_form = '''INSERT INTO city (city ,airport_id ) VALUES (%s, %s)'''
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
        self.my_cursor.executemany(currency_form, curr_list)
        self.my_cursor.executemany(city_form, city_list)
        self.my_cursor.executemany(place_form, data_prep_list)

        self.my_db.commit()

    def update_city(self, city, df_new):
        # Extrating data from DB
        try:
            city = re.search(r'([a-z-]*)-apartments', city).group(1)
        except:
            self.log.error('find city with regular expression failed')
            city = city

        # currency
        curr_list = df_new['currency'].unique()
        curr_dic = self.currency_verification(curr_list)

        # place and cities
        data = self.prep_data(df_new, curr_dic)
        city_dic = self.prep_data_city(data)
        self.city_verification(city, city_dic)

        place_db = self.get_query_df(f'SELECT * FROM place where city = "{city}"')

        to_delete = place_db[~place_db['page_link'].isin(data['page_link'])]
        to_update = data[data['page_link'].isin(place_db['page_link'])]
        to_insert = data[~data['page_link'].isin(place_db['page_link'])]

        to_delete = self.fix_df(to_delete)
        self.delete_old_row_in_db(to_delete)
        to_update = self.fix_df(to_update)
        self.update_homes_in_db(to_update)
        to_insert = self.fix_df(to_insert)
        self.insert_new_home(to_insert)

    def insert_new_home(self, to_update):
        # set-up lists:
        place_max_id = self.get_query_df(f'SELECT max(home_id) as id FROM place ')['id'].max()
        to_update.insert(0, 'home_id', 0)
        to_update = self.fix_df(to_update)

        for ind in to_update.index:
            place_max_id += 1
            to_update.loc[ind, 'home_id'] = place_max_id
        place_form = '''INSERT INTO place (
                                home_id,
                                city ,
                                page_link ,
                                sleeps ,
                                area_sqm ,
                                bedrooms , 
                                bathroom ,
                                price ,
                                currency ) VALUES (%s, %s,%s,%s,%s, %s, %s, %s, %s)'''
        self.my_cursor.executemany(place_form, to_update.values.tolist())
        # print("UPDATE : affected rows = {}".format(self.my_cursor.rowcount))
        self.my_db.commit()

    def fix_df(self, to_update):
        fixed_df = to_update.copy()
        fixed_df[['city', 'page_link', 'currency']] = fixed_df[['city', 'page_link', 'currency']].fillna('unknown',
                                                                                                         axis=1)
        fixed_df[['sleeps', 'area_sqm', 'bedrooms', 'bathroom', 'price']] = fixed_df[
            ['sleeps', 'area_sqm', 'bedrooms', 'bathroom', 'price']].fillna(0, axis=1)
        fixed_df.replace(to_replace ="null", value ="0", inplace=True)
        return fixed_df

    def update_homes_in_db(self, to_update):
        sql = '''UPDATE place SET sleeps= %s , area_sqm = %s, bedrooms = %s, 
                                            bathroom = %s, price = %s,
                                            currency= %s WHERE page_link = %s'''
        for ind in to_update.index:
            val = (str(to_update['sleeps'][ind]), str(to_update['area_sqm'][ind]), str(to_update['bedrooms'][ind]),
                   str(to_update['bathroom'][ind]), str(to_update['price'][ind]), str(to_update['currency'][ind]),
                   str(to_update['page_link'][ind]))
            self.my_cursor.execute(sql, val)
        self.my_db.commit()

    def delete_old_row_in_db(self, to_delete):
        for i in to_delete['page_link'].unique():
            delete_str = f'DELETE FROM place WHERE page_link ="{i}"'
            self.my_cursor.execute(delete_str)
        self.my_db.commit()

    def city_verification(self, city, city_dic):
        city_db = self.get_query_df(f'SELECT * FROM city where city = "{city}"')
        for i in city_dic.keys():
            if not i in city_db['city'].unique():
                city_form = '''INSERT INTO city (city ,airport_id ) VALUES (%s, %s)'''
                self.my_cursor.execute(city_form, [i, city_dic[i]])
                self.my_db.commit()

    def currency_verification(self, curr_list):
        curr_db = self.get_query_df(f'SELECT * FROM currency')
        curr_max_id = curr_db['id'].max()

        tmp_dic = curr_db.set_index('name').T.to_dict()
        return_dic = {i: tmp_dic[i]['id'] for i in tmp_dic.keys()}
        for i in curr_list:
            if not i in curr_db['name'].unique():
                currency_form = '''INSERT INTO currency (id ,name ) VALUES (%s, %s)'''
                curr_max_id += 1
                self.my_cursor.execute(currency_form, [str(curr_max_id), i])
                return_dic[i] = curr_max_id
                self.my_db.commit()
        return return_dic

    def update_city2(self, city, df_new):
        '''TO DELETE'''
        df_new = df_new.drop_duplicates(['page_link'])

        personal_debug.pd_loop(df_new, 'get inside update_city()')
        # Delete apartments that are no longer in the page

        try:
            df_old = self.get_query_df(
                'SELECT * FROM place WHERE city = "https://www.waytostay.com/' + city + '-apartments/"')
            df_old = df_old.drop_duplicates(['page_link'])

        except mysql.connector.errors.InternalError:
            self.log.error('Inserting new city')
            df_old = pd.DataFrame()
            print('Inserting new city')

        new_apartments = (str(list(df_new['page_link'].values))).strip('[]')

        if not df_old.empty:
            query_1 = "DELETE FROM place WHERE page_link NOT IN ({0})".format(new_apartments)
            query_1 += 'and city = "https://www.waytostay.com/' + city + '-apartments/"'
            self.my_cursor.execute(query_1)

        # Insert new apartments
        num_col = df_new.columns
        if not df_old.empty:
            df_insert = df_new.merge(df_old, on='page_link', how='left', indicator=True).query(
                '_merge == "left_only"').drop('_merge', 1)
            df_insert = df_insert[df_insert.columns[0:len(df_new.columns)]]
            df_insert.columns = num_col
            personal_debug.pd_loop(df_insert, 'ligne 100')
        else:
            df_insert = df_new
        data, data_prep_list, curr_list = self.prep_data(df_insert)
        personal_debug.pd_loop(data, 'ligne 104')
        personal_debug.pd_loop(data_prep_list, 'ligne 105')
        personal_debug.pd_loop(curr_list, 'ligne 106')

        try:
            self.my_cursor.execute("SELECT MAX(home_id) FROM place")
            max_id = self.my_cursor.fetchall()
            for i in range(max_id[0][0] + 1, max_id[0][0] + 1 + len(data_prep_list)):
                data_prep_list[i - max_id[0][0] - 1].insert(0, i)
            personal_debug.pd_loop(data_prep_list, 'ligne 113')

        except TypeError:
            self.log.error('type error on finding the max home_id')
            for i in range(len(data_prep_list)):
                data_prep_list[i].insert(0, i)
            personal_debug.pd_loop(data_prep_list, 'ligne 118')

        except mysql.connector.errors.InternalError:
            self.log.error('sql error on finding the max home_id')
            for i in range(len(data_prep_list)):
                data_prep_list[i].insert(0, i)
            personal_debug.pd_loop(data_prep_list, 'ligne 124')

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
        self.my_cursor.executemany(query_2, data_prep_list)
        self.my_db.commit()

        # Update apartments whose data has been changed

        if not df_old.empty:
            personal_debug.pd_loop(df_new, 'ligne 142')
            personal_debug.pd_loop(df_old, 'ligne 143')
            df_update = df_new.merge(df_old, on='page_link', how='inner', indicator=True)
            # df_update = pd.concat()
            df_update = df_update[df_update.columns[0:len(df_new.columns)]]
            df_update.columns = num_col
            personal_debug.pd_loop(df_update, 'ligne 147')

            upd_apartments = (str(list(df_update['page_link'].values))).strip('[]')
            query_3 = "DELETE FROM place WHERE page_link NOT IN ({0})".format(upd_apartments)
            self.my_cursor.execute(query_3)

            data, data_prep_list, curr_list = self.prep_data(df_update)
            personal_debug.pd_loop(data, 'ligne 153')
            personal_debug.pd_loop(data_prep_list, 'ligne 154')
            personal_debug.pd_loop(curr_list, 'ligne 155')

            self.my_cursor.execute("SELECT MAX(home_id) FROM place")
            max_id = self.my_cursor.fetchall()
            for i in range(max_id[0][0] + 1, max_id[0][0] + 1 + len(data_prep_list)):
                data_prep_list[i - max_id[0][0] - 1].insert(0, i)
            personal_debug.pd_loop(data_prep_list, 'ligne 162')

            query_4 = """INSERT INTO place (
                                            home_id,
                                            city ,
                                            page_link ,
                                            sleeps ,
                                            area_sqm ,
                                            bedrooms , 
                                            bathroom ,
                                            price ,
                                            currency_ID ) VALUES (%s, %s,%s,%s,%s, %s, %s, %s, %s)"""
            self.my_cursor.executemany(query_4, data_prep_list)
        self.my_db.commit()

    def update_global(self, df_new):
        try:
            self.my_cursor.execute("SELECT MAX(home_id) FROM place")
        except mysql.connector.errors.InternalError:
            self.log.error('DB does not exist')
            self.create_db()
            self.log.info('DB created')
            self.create_tables()
            self.log.info('tables created')
        finally:
            for city in df_new['city'].unique():
                print(city)
                city_name = re.search(r'https://www.waytostay.com/([a-z-]*)-apartments/', str(city)).group(1)
                print(city_name)
                self.update_city(city_name, df_new[df_new['city'] == city])
                self.log.info('City ' + city_name + ' has been updated in the database')

    def get_query_df(self, query):
        df = pd.read_sql_query(query, self.my_db)
        return df

    def prep_data2(self, data):
        '''TO DELETE'''
        # prepare the data:
        data = data.drop_duplicates(['page_link'])
        data = data.fillna(-1)
        # currency:
        curr_unique = data['currency'].unique().tolist()
        curr_list = [[i, curr_unique[i]] for i in range(len(curr_unique))]
        curr = {i[1]: i[0] for i in curr_list}

        # other :
        data['currency'] = data['currency'].apply(lambda x: curr[x])
        data['bedrooms'] = data['bedrooms'].apply(lambda x: int(x) if x != 'studio' else 0)
        data_prep_list = data.values.tolist()

        return data, data_prep_list, curr_list

    def prep_data(self, data, curr):
        # prepare the data:
        data = data.drop_duplicates(['page_link'])
        data = data.fillna(-1)
        data['city'] = data['city'].map(lambda x: re.search(r'([a-z-]*)-apartments', x).group(1))

        # other :
        data['currency'] = data['currency'].apply(lambda x: curr[x])
        data['bedrooms'] = data['bedrooms'].apply(lambda x: int(x) if x != 'studio' else 0)

        # return data, data_prep_list, curr_list
        return data

    def prep_data_currency(self, data):
        df_curr = data['currency'].unique()
        curr_unique = df_curr.tolist()
        curr_list = [[i, curr_unique[i]] for i in range(len(curr_unique))]
        curr = {i[1]: i[0] for i in curr_list}
        return curr

    def prep_data_city(self, data):
        fly = Fly()

        # cities:
        df_city = data['city'].unique()
        city_dictionary = {}
        for i in list(data['city'].unique()):
            try:
                city_dictionary[i] = fly.find_airport_by_city_name(i)
            except:
                city_dictionary[i] = ' '
                print(i, 'airport not found')
                self.log.error('airport not found')

        '''city_dictionary = {'paris': 'ORY', 'berlin': 'TXL', 'barcelona': 'BCN', 'lisbon': 'LIS', 'florence': 'FLR',
                           'rome': 'CIA', 'london': 'LCY', 'madrid': 'MAD', 'prague': 'PRG', 'valencia': 'VLC',
                           'brussels': 'BRU', 'istanbul': 'ISL', 'seville': 'SVQ', 'vienna': 'VIE', 'budapest': 'BUD',
                           'milan': 'LIN', 'porto': 'OPO', 'warsaw': 'WAW', 'krakow': 'KRK', 'albufeira': 'FAO',
                           'almancil': 'FAO', 'coast': 'SYY', 'andalusia': 'GRX', 'andorra': 'LEU', 'antibes': 'JCA',
                           'arachova': 'GPA', 'pera': 'IPH', 'athens': 'AHN', 'avignon': 'AVN', 'benavente': 'VLL',
                           'bolonia': 'BLQ', 'bordeaux': 'BOD', 'island': 'AEY', 'buarcos': 'VSE', 'caceres': 'BJZ',
                           'cadiz': 'XRY', 'canneddi': 'OLB', 'cannes': 'JCA', 'carrapateira': 'JDO', 'carvoeiro': 'PRM',
                           'cascais': 'CAT', 'mediano': 'PMF', 'cordoba': 'SVQ', 'dampezzo': 'BZO', 'blanca': 'FRS',
                           'brava': 'SFL', 'sol': 'GMP', 'dinard': 'DNR', 'dubai': 'DWC', 'dubrovnik': 'DBV',
                           'romagna': 'FRL', 'ericeira': 'CAT', 'faro': 'FAE', 'foz': 'LCG', 'fuerteventura': 'FUE',
                           'gandia': 'VLC', 'genoa': 'GOA', 'gozo': 'GZM', 'canaria': 'ANS', 'hvar': 'BWK', 'istria': 'PUY',
                           'frontera': 'LOV', 'gulf': 'ECP', 'lagos': 'LOS', 'como': 'LUG', 'garda': 'VRN',
                           'lanzarote': 'ACE', 'liguria': 'GOA', 'lombardia': 'BGY', 'madeira': 'FNC', 'malaga': 'AGP',
                           'malta': 'MLA', 'marbella': 'AGP', 'marseille': 'MRS', 'minturno': 'NAP', 'gordo': 'SLM',
                           'nantes': 'NTE', 'naples': 'NAP', 'nice': 'NCE', 'porches': 'PRM', 'portimao': 'PRM',
                           'cervo': 'ALL', 'puglia': 'BRI', 'quarteira': 'FAO', 'rennes': 'RNS', 'mouro': 'PRM',
                           'sebastian': 'FSM', 'sardinia': 'TTB', 'seghe': 'BZO', 'sicily': 'CTA', 'sintra': 'CAT',
                           'sitges': 'BCN', 'skiathos': 'JSI', 'split': 'SPU', 'tarragona': 'REU', 'tavira': 'FAO',
                           'tenerife': 'TFS', 'thessaloniki': 'SKG', 'toulouse': 'TLS', 'trieste': 'TRS', 'tuscany': 'FLR',
                           'umbria': 'PEG', 'daosta': 'TRN', 'veneto': 'TSF', 'venice': 'VCE', 'verona': 'VRN',
                           'vilamoura': 'FAO', 'zavala': 'SJJ'}'''
        return city_dictionary
