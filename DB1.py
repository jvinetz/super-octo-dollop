import DB
import pandas as pd

df = pd.read_csv(r'csv/data.csv')
df = df.values.tolist()
#print(df['curency'].unique())
DB.first_fill(df)
