import re
import pandas as pd
from dateutil import parser

#  Tlog data
df = pd.read_csv(r"Output/Processed_Data/transactions.csv")
df2 = pd.read_csv(r"Output/Processed_Data/unsync_balance_transactions.csv")

excel_file = 'Output/Report.xlsx'

# Convert relevant columns to numeric types
df[['amount', 'vat', 'oldBalance', 'newBalance']] = df[['amount', 'vat', 'oldBalance', 'newBalance']].apply(pd.to_numeric)
df2[[ 'subscriptionBalance', 'paymentBalance']] = df2[['subscriptionBalance', 'paymentBalance']].apply(pd.to_numeric)

# Detect overdrafts 
df['overdraft'] = ((df['amount'] + df['vat']) - df['oldBalance']) 

# Filter the transactions with overdraft
overdraft_transactions = df[df['overdraft'] > 0]

# Detect inconsistent balances
df['inconsistent_balance'] = df['newBalance'] != (df['oldBalance'] + df['amount'] - df['vat'])

# Detect large transactions
threshold_large_amount = df['amount'].mean() + 3 * df['amount'].std()  # Example threshold
df['large_transaction'] = df['amount'] > threshold_large_amount

# Detect unusual VAT amounts
expected_vat_rate = 0.05  # Example VAT rate
df['unusual_vat'] = df['vat'] != (df['amount'] * expected_vat_rate)


# Detect timestamp anomalies (assuming business hours 9 AM to 5 PM UTC for example)

# Convert the timestamp column to datetime using dateutil
df["timestamp"] = df["timestamp"].apply(parser.parse)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['unusual_time'] = ~df['timestamp'].dt.hour.between(9, 17)

# Save to CSV for further analysis
#df.to_csv('subscriber_balances_anomalies.csv', index=False)

# Print the DataFrame with anomalies
#print(df)

# Print rows with any anomalies
anomalies = df[
    (df['overdraft'].astype(bool)) |
    (df['inconsistent_balance'].astype(bool)) |
    (df['large_transaction'].astype(bool)) |
    (df['unusual_vat'].astype(bool)) |
    (df['unusual_time'].astype(bool))
]
#print("\nAnomalies:\n", anomalies)

# Merge the Anomalies Transactions to a new sheet 

with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df['timestamp'] = df['timestamp'].dt.tz_localize(None)  #  df['unusual_time'].dt.date
    df.to_excel(writer, sheet_name='Anomalies', index=False)    
print('Done')