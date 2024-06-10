import pandas as pd
import ast
import numpy as np

df = pd.read_csv(r"Output/Processed_Data/transactions.csv")
df2 = pd.read_csv(r"Output/Processed_Data/unsync_balance_transactions.csv")

# removing any duplicate rows
df = df.drop_duplicates()
df2 = df2.drop_duplicates()

# remove unwanted characters from the amount field
df['amount'] = df['amount'].str.replace('[\$,€,£]', '', regex=True)
df['vat'] = df['vat'].str.replace('[\$,€,£]', '', regex=True)
df['oldBalance'] = df['oldBalance'].str.replace('[\$,€,£]', '', regex=True)

df2['subscriptionBalance'] = df2['subscriptionBalance'].str.replace('[\$,€,£]', '', regex=True)

# convert the amount field to decimal
df['amount'] = pd.to_numeric(df['amount'], errors='coerce').round(3)
df['vat'] = pd.to_numeric(df['vat'], errors='coerce').round(2)
df['oldBalance'] = pd.to_numeric(df['oldBalance'], errors='coerce').round(3)
df['newBalance'] = pd.to_numeric(df['newBalance'], errors='coerce').round(3)

df2['subscriptionBalance'] = pd.to_numeric(df2['subscriptionBalance'], errors='coerce').round(3)
df2['paymentBalance'] = pd.to_numeric(df2['paymentBalance'], errors='coerce').round(3)

# remove commas from the string column
df['currency'] = df['currency'].str.replace(',', '')
df['id'] = df['id'].str.replace(',', '')
df['userId'] = df['userId'].str.replace(',', '')

df2['userId'] = df2['userId'].str.replace(',', '')

# convert into timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
df2['timestamp'] = pd.to_datetime(df2['timestamp'])
df2['timestamp'] = pd.to_datetime(df2['timestamp'], format='%Y-%m-%d %H:%M:%S')
# save the DataFrame to a CSV file
df.to_csv("Output/Processed_Data/transactions.csv", index=False)
df2.to_csv("Output/Processed_Data/unsync_balance_transactions.csv", index=False)
print('Done')
