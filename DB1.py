import DB
import pandas as pd

data = pd.read_csv(r'csv/data1.csv')
data = data.iloc[:,1:]
'''print(data)

curr_unique = data['curency'].unique().tolist()
curr_list = [[i, curr_unique[i]] for i in range(len(curr_unique))]
curr = {i[1]: i[0] for i in curr_list}

data['curency'] = data['curency'].apply(lambda x: curr[x])
data['bedrooms'] = data['bedrooms'].apply(lambda x: int(x) if x != 'studio' else 0)
data_prep_list = data.values.tolist()
for i in range(len(data_prep_list)):
    data_prep_list[i].insert(0, i)
print(data_prep_list)'''

DB.first_fill(data)
