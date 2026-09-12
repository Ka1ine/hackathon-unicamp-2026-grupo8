# launch script from repository root

import pandas as pd

df1 = pd.read_csv('data/sentencas.csv')
df2 = pd.read_csv('data/subsidios.csv')

key_column = df1.columns[0]

merged_df = pd.merge(df1, df2, on=key_column, how='inner')
merged_df.to_csv('combined.csv', index=False)
merged_df.head()