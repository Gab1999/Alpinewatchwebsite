import sqlite3
import pandas as pd
import os

# Paths
db_path = "alpinewatch.db"
glacier_clean_path = os.path.join("Data", "glacier_data_clean.csv")
ghg_clean_path = os.path.join("Data", "ghg_data_clean.csv")

#new schema changes
if os.path.exists(db_path):
    try:
        os.remove(db_path)
    except PermissionError:
        pass

#Database connect 
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

#tables (data) 

#Countries table 
 #IF NOT EXISTS means i can run the code multiple times as it wont recreate the table. (To force create table each time i change to DROP TABLE)
 #IPKA assigns unique id to datapoints 
 #No duplicates and required for unique not null
cursor.execute('''
CREATE TABLE IF NOT EXISTS countries ( 
    country_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    country_name TEXT UNIQUE NOT NULL 
)
''')

#Glaciers table 
#UNIQUE constraint so each glacier appears once per country
cursor.execute('''
CREATE TABLE IF NOT EXISTS glaciers (
    glacier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    glacier_name TEXT NOT NULL,
    country_id INTEGER NOT NULL,
    UNIQUE(glacier_name, country_id),
    FOREIGN KEY (country_id) REFERENCES countries(country_id) 
    )
''')
# now i can't add a glacier with a country_id that doesn't exist (FK)


#Glacier data table
#No autoincrement for glac_id cuz already links to glacier table (where ids made)
#Real lets store number with decimal
#UNIQUE constraint for one measurement per glacier-year
cursor.execute('''
CREATE TABLE IF NOT EXISTS glacier_data (
    glacier_data_id INTEGER PRIMARY KEY AUTOINCREMENT,
    glacier_id INTEGER NOT NULL, 
    year INTEGER NOT NULL,
    net_mass_balance REAL, 
    UNIQUE(glacier_id, year),
    FOREIGN KEY (glacier_id) REFERENCES glaciers(glacier_id)
)
''')

#GHG table 
#UNIQUE constraint for one record per country-year
cursor.execute('''
CREATE TABLE IF NOT EXISTS ghg_emissions (
    ghg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    emissions_index REAL,
    UNIQUE(country_id, year),
    FOREIGN KEY (country_id) REFERENCES countries(country_id)
)
''')


#Loading datsa 

glacier_df = pd.read_csv(glacier_clean_path)

#Unique countries into countries table
unique_countries = glacier_df['country'].unique()
for country in unique_countries:
    try:
        cursor.execute("INSERT INTO countries (country_name) VALUES (?)", (country,)) #SQL query 
    except sqlite3.IntegrityError: #Integrity error = when country being inserted already exists so pass ignores it. 
        pass  

conn.commit() #Saved to db permanently 
print(f" {len(unique_countries)} countries added")

#Unique glaciers into glaciers table
#inserting unique glacier-country pairs only once
unique_glaciers = glacier_df[['glacier_name', 'country']].drop_duplicates()
for idx, row in unique_glaciers.iterrows(): #loops through all row numbers (idx) and iterrows loops through rows of df
    glacier_name = row['glacier_name']
    country_name = row['country']
    
    #country_id
    cursor.execute("SELECT country_id FROM countries WHERE country_name = ?", (country_name,))
    country_id = cursor.fetchone()[0]  #first result as tuple, [0]first element 
    
    #galcier name and country id insert 
    try:
        cursor.execute(
            "INSERT INTO glaciers (glacier_name, country_id) VALUES (?, ?)",
            (glacier_name, country_id)
        )
    except sqlite3.IntegrityError:
        pass

conn.commit()

#Getting and inserting glacier data 
for idx, row in glacier_df.iterrows(): 
    glacier_name = row['glacier_name']
    country_name = row['country'] # [FIXED] Added country context for precise lookup
    year = int(row['year'])
    net_mass_balance = row['net_mass_balance']
    
    #Get glacier_id from glacier name 
    #lookup uses both name and country for relational 
    cursor.execute("""
        SELECT g.glacier_id 
        FROM glaciers g
        JOIN countries c ON g.country_id = c.country_id
        WHERE g.glacier_name = ? AND c.country_name = ?
    """, (glacier_name, country_name))
    
    result = cursor.fetchone()
    if result:
        glacier_id = result[0]
        try:
            cursor.execute(
                "INSERT INTO glacier_data (glacier_id, year, net_mass_balance) VALUES (?, ?, ?)",
                (glacier_id, year, net_mass_balance)
            )
        except sqlite3.IntegrityError:
            pass #Skip dupes for same glacier-year

conn.commit()
print(f"{len(glacier_df)} glacier measurements processed")

#ghg 
ghg_df = pd.read_csv(ghg_clean_path)

unique_ghg_countries = ghg_df['country'].unique()
for country in unique_ghg_countries:
    try:
        cursor.execute("INSERT INTO countries (country_name) VALUES (?)", (country,))
    except sqlite3.IntegrityError:
        pass  

conn.commit()


#ghg 
for idx, row in ghg_df.iterrows():
    country_name = row['country']
    year = int(row['year'])
    emissions_index = row['emissions_index']
    
     
    cursor.execute("SELECT country_id FROM countries WHERE country_name = ?", (country_name,))
    country_id= cursor.fetchone()[0]
    try:
        cursor.execute(
                "INSERT INTO ghg_emissions (country_id, year, emissions_index) VALUES (?, ?, ?)",
                (country_id, year, emissions_index)
            )
    except sqlite3.IntegrityError:
        pass #Skip dupes for same country-year

conn.commit()
print(f" {len(ghg_df)} GHG emission records processed")


#Check data
cursor.execute("SELECT COUNT(*) FROM countries")
country_count = cursor.fetchone()[0]
print(f"Total countries: {country_count}")

cursor.execute("SELECT COUNT(*) FROM glaciers")
glacier_count = cursor.fetchone()[0]
print(f"Total unique glaciers: {glacier_count}") #sshows unique count

cursor.execute("SELECT COUNT(*) FROM glacier_data")
glacier_data_count = cursor.fetchone()[0]
print(f"Total glacier measurements: {glacier_data_count}")

cursor.execute("SELECT COUNT(*) FROM ghg_emissions")
ghg_count = cursor.fetchone()[0]
print(f"Total GHG records: {ghg_count}")

conn.close() 

print(f"\nDatabase file: {db_path}")
