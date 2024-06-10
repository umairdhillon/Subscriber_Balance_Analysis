import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.chart import LineChart, Reference, Series
from dateutil import parser
import plotly.graph_objects as go


df = pd.read_csv(r"Output/Processed_Data/transactions.csv")
df2 = pd.read_csv(r"Output/Processed_Data/unsync_balance_transactions.csv")

excel_file = 'Output/Report.xlsx'

#Credit Mismatch information after a Debit transaction

df['overdraft'] = ((df['amount'] + df['vat']) - df['oldBalance']) 

# Filter the transactions with overdraft
overdraft_transactions = df[df['overdraft'] > 0]


# Write the data to an Excel file
df.to_excel(excel_file, index=False)

# Save the overdraft transactions to a new sheet 
with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    overdraft_transactions.to_excel(writer, sheet_name='Overdraft Transactions', index=False)
    
# Merge the Out of Sunc Balance Transactions to a new sheet 
with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df2.to_excel(writer, sheet_name='erroneous Transactions', index=False)

#print('Done')

########################################################## PAYMENT HISTORY over Running Balance #############################################

# Load the data
draft_df = pd.read_csv('Output/Processed_Data/unsync_balance_transactions.csv')
transactions_df = pd.read_csv('Output/Processed_Data/transactions.csv')

excel_file = 'Output/Visualization/Payment_History_Report.xlsx'
# Merge the data
merged_df = pd.merge(draft_df, transactions_df, on=['userId', 'timestamp'])

# Calculate running balance
merged_df['running_balance'] = merged_df.groupby('userId')['amount'].cumsum()

# Identify overdrafts
merged_df['overdraft'] = merged_df['running_balance'] < 0

# Visualize payment history
plt.figure(figsize=(12, 6))
sns.lineplot(x='timestamp', y='running_balance', hue='userId', data=merged_df)
plt.title('Payment History')
plt.xlabel('Timestamp')
plt.ylabel('Running Balance')
#plt.show()

# Anomaly detection
merged_df['anomaly'] = merged_df['amount'] > merged_df['amount'].mean() + 3 * merged_df['amount'].std()

# Flag anomalies
anomalies = merged_df[merged_df['anomaly'] == True]

# Create an Excel file with a chart
with pd.ExcelWriter(excel_file, engine='xlsxwriter',) as writer:
    anomalies.to_excel(writer, sheet_name='Report', index=False)
    
    # Create a chart
    workbook = writer.book
    worksheet = writer.sheets['Report']
    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({
        'categories': '=Anomalies!$A$2:$A$' + str(len(anomalies) + 1),
        'values': '=Anomalies!$B$2:$B$' + str(len(anomalies) + 1),
    })
    chart.set_title({'name': 'Anomaly Detection'})
    chart.set_x_axis({'name': 'Timestamp'})
    chart.set_y_axis({'name': 'Amount'})
    worksheet.insert_chart('D2', chart)
    
#print('Done')
########################################################## Unsync PAYMENT HISTORY Over PAYMENT BALANCE #############################################

# Load the data
draft_df = pd.read_csv('Output/Processed_Data/unsync_balance_transactions.csv')

# Create a new Excel file
wb = Workbook()
ws = wb.active

# Create the chart
plt.figure(figsize=(12, 6))

for userId, group in draft_df.groupby('userId'):

    plt.plot(group['timestamp'], group['paymentBalance'], label=userId)

plt.title('Payment History')
plt.xlabel('Timestamp')
plt.ylabel('paymentBalance')
plt.legend()

# Save the chart to a file
plt.savefig('chart.png')

# Add the chart to the Excel file
img = Image('chart.png')
ws.add_image(img, 'A1')

# Save the Excel file
wb.save('Output/Visualization/Unsync_Payment_trend.xlsx')

########################################################## Daily Balance #############################################

# Convert the timestamp column to datetime using dateutil
df["timestamp"] = df["timestamp"].apply(parser.parse)

# Set the timestamp column as the index
df.set_index("timestamp", inplace=True)

# Group the data by userId and resample by day
daily_balance = df.resample("D").apply(lambda x: x["newBalance"].iloc[-1] if len(x) > 0 else None)

# Remove timezone information from the datetime values

daily_balance.index = daily_balance.index.tz_localize(None)

# Create an ExcelWriter object
with pd.ExcelWriter('Output/Visualization/daily_balance_trend.xlsx', engine='openpyxl') as writer:

    # Write the data to the Excel file
    daily_balance.to_excel(writer, header=True, index=True)

    # Get the worksheet object
    workbook = writer.book
    worksheet = workbook.active

    # Create a line chart
    chart = LineChart()
    chart.title = "Daily Balance Trend"
    chart.style = 13
    chart.x_axis.title = "Date"
    chart.y_axis.title = "Balance"

    # Select the data range for the chart
    data = Reference(worksheet, min_row=1, max_row=len(daily_balance) + 1, min_col=1, max_col=2)

    # Add the data series to the chart
    series = Series(data, title="Daily Balance")
    chart.append(series)

    # Add the chart to the worksheet
    worksheet.add_chart(chart, "E2")

########################################################## Payment History Over Time  #############################################

# Load the payment history data
df = pd.read_csv(r"Output/Processed_Data/transactions.csv")

# Convert the timestamp column to datetime using dateutil
df["timestamp"] = df["timestamp"].apply(parser.parse)
df['timestamp'] = pd.to_datetime(df['timestamp'])
# Set the timestamp column as the index
df.set_index("timestamp", inplace=True)

df.index = df.index.tz_localize(None)

# Calculate the total payment amount by month

monthly_payments = df.resample("M")["amount"].sum()

# Plot the monthly payment trend using Matplotlib
plt.figure(figsize=(10, 6))
plt.plot(monthly_payments.index, monthly_payments.values)
plt.title("Monthly Payment Trend")
plt.xlabel("Month")
plt.ylabel("Total Payment Amount")


# Plot the payment distribution using Seaborn

plt.figure(figsize=(10, 6))
sns.displot(df["amount"], kde=False)
plt.title("Payment Distribution")
plt.xlabel("Payment Amount")
plt.ylabel("Frequency")


# Create an interactive plot using Plotly
fig = go.Figure(data=[go.Bar(x=monthly_payments.index, y=monthly_payments.values)])
fig.update_layout(title="Monthly Payment Trend", xaxis_title="Month", yaxis_title="Total Payment Amount")

# Create an Excel file

with pd.ExcelWriter('Output/Visualization/Payments.xlsx') as writer:

    # Write the monthly payment trend to a sheet
    monthly_payments.to_excel(writer, sheet_name='Monthly Payment Trend')
    # Write the payment distribution to another sheet
    payment_distribution = df["amount"].value_counts().reset_index()
    payment_distribution.columns = ['Payment Amount', 'Frequency']
    payment_distribution.to_excel(writer, sheet_name='Payment Distribution')

    # Write the original data to another sheet
    df.reset_index().to_excel(writer, sheet_name='Original Data')

print('Done')