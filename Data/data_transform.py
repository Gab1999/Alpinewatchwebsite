import pandas as pd
import os

# Define file paths
data_folder = "Data"
glacier_file = os.path.join(data_folder, "cumulative-specific-net-mass-balance-2.csv")
ghg_file = os.path.join(data_folder, "ee25-total-greenhouse-gas-emissions-all-eea38-countries.csv")



# TRANFORMING GLACIER DATA
glacier_df = pd.read_csv(glacier_file)
glacier_df = glacier_df.dropna(how='all')

# wide to long 
glacier_long = glacier_df.melt(
    id_vars=['Year:year'],
    var_name='glacier_info',
    value_name='net_mass_balance'
)

# Rename columns
glacier_long.columns = ['year', 'glacier_info', 'net_mass_balance']

# glacier name and country from glacier_info as "Glacier Name (Country):number"
glacier_long[['glacier_name', 'country_info']] = glacier_long['glacier_info'].str.split(':', n=1, expand=True)
glacier_long['country_info'] = glacier_long['country_info'].str.strip()

# Extracting country and glacier name 
glacier_long['country'] = glacier_long['glacier_name'].str.extract(r'\(([^)]+)\)')[0] #Extract the text inside parentheses () so country. ([^)]+) = Capture group: match any characters that are NOT ). [0] = first and only captured grp
glacier_long['glacier_name'] = glacier_long['glacier_name'].str.extract(r'^([^(]+)')[0].str.strip() #Same but ^is the start of the string so extracts text that isnt ) but starting outside the parenthases so first word ([0]) is glacier name

# Keep only columns I want
glacier_long = glacier_long[['year', 'glacier_name', 'country', 'net_mass_balance']]

# Remove glaciers without data for that year
glacier_clean = glacier_long.dropna(subset=['net_mass_balance'])

print(f"Transformed glacier data shape: {glacier_clean.shape}")
print("\nFirst 10 rows of transformed glacier data:")
print(glacier_clean.head(10))

# Save cleaned data
glacier_clean.to_csv(os.path.join(data_folder, "glacier_data_clean.csv"), index=False)
print(f"\n saved to path: {os.path.join(data_folder, 'glacier_data_clean.csv')}")


#TRANSFORMING GHG DATA
ghg_df = pd.read_csv(ghg_file)
ghg_df = ghg_df.dropna(how='all')

# Keep only years till 2023 
ghg_df = ghg_df[ghg_df['years'] <= 2023]

# only extracting years (rows) for 4 "countries"
countries_of_interest = ['Switzerland', 'Italy', 'France', 'EU']
ghg_columns = ['years']

# Find columns for countries of interest
for col in ghg_df.columns:
    for country in countries_of_interest:
        if country in col and 'trend_Total_greenhouse_gas_emissions' in col:
            ghg_columns.append(col)

ghg_subset = ghg_df[ghg_columns]

# wide to long
ghg_long = ghg_subset.melt(
    id_vars=['years'],
    var_name='country_col',
    value_name='emissions_index'
)

# country name from column name
ghg_long['country'] = ghg_long['country_col'].str.split('_trend_', n=1).str[0]

# Keep columns i want
ghg_long = ghg_long[['years', 'country', 'emissions_index']]
ghg_long.columns = ['year', 'country', 'emissions_index']

# Remove rows with No values 
ghg_clean = ghg_long.dropna(subset=['emissions_index'])


print(f"Transformed GHG data shape: {ghg_clean.shape}")
print("\nFirst 10 rows of transformed GHG data:")
print(ghg_clean.head(10))

# Save cleaned GHG data
ghg_clean.to_csv(os.path.join(data_folder, "ghg_data_clean.csv"), index=False)
print(f"\n✓ Saved to: {os.path.join(data_folder, 'ghg_data_clean.csv')}")

#Done 
print(f"\nClean files saved to: {data_folder}/")
