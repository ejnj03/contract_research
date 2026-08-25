import csv

file_path = 'storage_dict_update.csv'  # Specify the path to your CSV file
headers = ['citation', 'model', 'response_number', 'response']

try:
    with open(file_path, 'w', newline='') as file:
        print(f"Opening file: {file_path}")
        writer = csv.writer(file)
        writer.writerow(headers)
        print(f"Written headers: {headers}")
except Exception as e:
    print(f"An error occurred: {e}")