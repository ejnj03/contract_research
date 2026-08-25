import pandas as pd
import csv


# Load the data
df = pd.read_csv('storage_dict.csv', quotechar='"', quoting=csv.QUOTE_MINIMAL)

print(df.head())

# Assuming you want to drop row indices that you manually deleted
#rows_to_delete = [22, 20]  # Example row indices
#df = df.drop(rows_to_delete, axis=0)

# Reset index if necessary
#df.reset_index(drop=True, inplace=True)

# Save back to CSV
#df.to_csv('storage_dict.csv', quotechar='"', quoting=csv.QUOTE_MINIMAL, index=False)

condition = (df['response_number'] == "second_input")
df = df[condition]
df.to_csv('storage_dict.csv', index=False)
df.reset_index(drop=True, inplace=True)

print(df.head())