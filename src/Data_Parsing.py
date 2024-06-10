import os
import gzip
import json
import csv
import re

def get_all_Transactions(root_folder):
    all_folders = []
    transactions = []
    out_of_sync_balance = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        all_folders.append(dirpath)
        all_folders.extend([os.path.join(dirpath, dirname) for dirname in dirnames])
        for name in filenames:
            if name == '000000.gz':
                file_path = os.path.join(dirpath, name)
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    file_content = f.read()
                    # Regular expression to find timestamps before "START RequestId:"
                    pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z) START RequestId:"
                    match = re.search(pattern, file_content)
                    if match:
                        timestamp = match.group()
                        timestamp = timestamp.split(' ')[0]
                        d = {'timestamp': timestamp}
                    #timestamps = re.findall(pattern, log_data)
                        transaction_pattern = re.compile(r'Start syncing the balance\s+{([^}]+)}', re.DOTALL)
                        for match in transaction_pattern.finditer(file_content):
                            transaction_block = match.group(1).strip()
                            transaction_dict = {}
                            for line in transaction_block.splitlines():
                                key, _, value = line.partition(':')
                                transaction_dict[key.strip()] = value.strip()
                                # Combine the transaction and timestamp into a single dictionary
                                transaction_dict['timestamp'] = timestamp
                            transactions.append(json.dumps(transaction_dict))                 
                        
                    transaction_pattern2 = re.compile(r'ERROR	Subscription balance and payment balance are not in sync\s+{([^}]+)}', re.DOTALL)
                    for match in transaction_pattern2.finditer(file_content):
                        transaction_block2 = match.group(1).strip()
                        transaction_dict2 = {}
                        for line in transaction_block2.splitlines():
                            key, _, value = line.partition(':')
                            transaction_dict2[key.strip()] = value.strip()
                            transaction_dict2['timestamp'] = timestamp
                        out_of_sync_balance.append(json.dumps(transaction_dict2))
                    
    return transactions,out_of_sync_balance

def write_transactions_to_csv(transactions, csv_file):
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["id", "userId", "currency", "amount", "vat", "oldBalance", "newBalance","timestamp"])
        writer.writeheader()
        for transaction in transactions:
            transaction_dict = json.loads(transaction)
            writer.writerow({
                "id": transaction_dict.get("id", ""),
                "userId": transaction_dict.get("userId", ""),
                "currency": transaction_dict.get("currency", ""),
                "amount": transaction_dict.get("amount", ""),
                "vat": transaction_dict.get("vat", ""),
                "oldBalance": transaction_dict.get("oldBalance", ""),
                "newBalance": transaction_dict.get("newBalance", ""),
                "timestamp": transaction_dict.get("timestamp", "")
            })
def Out_of_Sync_transactions(transactions, csv_file):
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["userId","subscriptionBalance","paymentBalance","timestamp"])
        writer.writeheader()
        for transaction in transactions:
            transaction_dict = json.loads(transaction)
            writer.writerow({
                "userId": transaction_dict.get("userId", ""),
                "subscriptionBalance": transaction_dict.get("subscriptionBalance", ""),
                "paymentBalance": transaction_dict.get("paymentBalance", ""),
                "timestamp": transaction_dict.get("timestamp", "")
            })

root_folder = "Logs/balance-sync-logs/balance-sync-logs"
transctions_file = "Output/Processed_Data/transactions.csv"
unsync_balance_transactions = "Output/Processed_Data/unsync_balance_transactions.csv"

get_all_Transactions = get_all_Transactions(root_folder)
#print(get_all_Transactions)
if get_all_Transactions:
    #print("Data Copied:")
    write_transactions_to_csv(get_all_Transactions[0], transctions_file)
    Out_of_Sync_transactions(get_all_Transactions[1], unsync_balance_transactions)
    print('Done')
else:
    print("No folders found in the specified path.")
