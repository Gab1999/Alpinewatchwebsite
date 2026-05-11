import pandas as pd
import os

# Define file paths
data_folder = "Data"  # Your Data folder
glacier_file = os.path.join(data_folder, "cumulative-specific-net-mass-balance-2.csv")
ghg_file = os.path.join(data_folder, "ee25-total-greenhouse-gas-emissions-all-eea38-countries.csv")


print("ALPINEWATCH Data Cleaning")

#GLACIER CELANING
glacier_df = pd.read_csv(glacier_file)
print(f"Original glacier data shape: {glacier_df.shape}")
print(f"Columns: {glacier_df.columns.tolist()}") #tolist() cleaner (no index() outside)

# dropna() (na = empty cell) to remove rows/columns with missing data and how='all' for rows where all columns are empty (Couldve used subset too)
glacier_df = glacier_df.dropna(how='all')

print("\nFirst 5 rows of glacier data:")
print(glacier_df.head())


#GHG CLEANING
ghg_df = pd.read_csv(ghg_file)
print(f"Original GHG data shape: {ghg_df.shape}")
print(f"Columns: {ghg_df.columns.tolist()}")

# kill empty cells again 
ghg_df = ghg_df.dropna(how='all')

print("\nFirst 5 rows of GHG data:")
print(ghg_df.head())




