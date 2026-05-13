This website explores glacier changes in the Alps alongside greenhouse gas emissions data. I focused on visualising how glacier mass balance has evolved over time in countries such as Switzerland, France, and Italy.

Data

All the datasets were cleaned and prepared using pandas before being inserted into the database.

Pandas was used for data cleaning and preprocessing
Cleaned datasets include:
Glacier mass balance data
Greenhouse gas emissions data
Data is stored in CSV files and loaded into a database


DataSets:

I will be implementing data from:

The European Environment Agency (https://www.eea.europa.eu/en/datahub) 

Eurostat (https://ec.europa.eu/eurostat/web/main/home) 

The Climate Change Indicators Dashboard (https://climatedata.imf.org/pages/access-data) 



Backend

Flask is used to: Handle routes (/, /quiz, /data, etc.), Process quiz submissions, Serve data to the frontend

SQLite3 is used to store: Countries, Glaciers, Glacier measurements, GHG emissions

The backend:
-Executes SQL queries to retrieve my aggregated data (tables)
-Retrieves time series data for visualisation (graph)
-Passes all data to HTML templates using Jinja2



Frontend

-Jinja2 dynamically renders HTML with backend data
-Plotly.js was used for the interactive graph: Glacier mass balance over time 
-HTML tables display: Glacier statistics by country, GHG emissions data, CSS is used for layout and styling



Components

Data Pipeline:
-Raw CSV files cleaned with pandas in python files
-Cleaned data is inserted into an SQLite database (alpinewatch.db)
-The database is then used by the Flask application


Data Page (/data)
-Browser sends a request (HTTP GET)
-Flask executes SQL queries: Aggregated glacier statistics (average mass balance), GHG emissions data, Glacier time-series data
-Data is passed to the data.html template
-Jinja2 injects data into the HTML and 
-Plotly.js renders the interactive graph in the browser


Quiz System (/quiz -> /submit-quiz)
User accesses the quiz page
Answers are submitted via POST request
Flask processes answers and calculates score
Results are displayed on the results page

Stack:
Python
Flask
SQLite3
Pandas
Plotly.js
HTML / CSS



Running:
pip install flask pandas
python Data_base.py
python app.py
http://127.0.0.1:5000
