import pandas as pd
import wget
from datetime import date
import joblib
import requests

# Remove any old COVID-19 data
import os
dirname = os.path.dirname(__file__)
try:
    os.remove(os.path.join(dirname, '../data/raw/COVID-19-geographic-disbtribution-worldwide.xlsx'))
except OSError:
    print("File not found")


# Download the latest data
covid_url = 'https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide.xlsx'
wget.download(covid_url, os.path.join(dirname, '../data/raw/COVID-19-geographic-disbtribution-worldwide.xlsx'))

# Read the data
eu_data = os.path.join(dirname, '../data/raw/COVID-19-geographic-disbtribution-worldwide.xlsx')
df = pd.read_excel(eu_data)

# What does the data contain
max_date = df.dateRep.max()
min_date = df.dateRep.min()

# Add World
world = df.groupby('dateRep').sum()
dfw = world[['cases', 'deaths', 'popData2018']]
dateRep_dt = world.index.to_list()
dateRep = [date.strftime('%Y-%m-%d') for date in dateRep_dt]
dfw['dateRep'] = dateRep
dfw['month'] = dfw['dateRep'].apply(lambda x: int(x[5:7]))
dfw['year'] = dfw['dateRep'].apply(lambda x: int(x[0:4]))
dfw['day'] = dfw['dateRep'].apply(lambda x: int(x[8:10]))
dfw['countriesAndTerritories'] = dfw['day'].apply(lambda x: 'World')
dfw['geoId'] = dfw['day'].apply(lambda x: 'World')
dfw['countryterritoryCode'] = dfw['day'].apply(lambda x: 'World')
df.drop(['continentExp'], axis=1, inplace=True)
dfw = dfw[df.columns]

# Put back World
df = pd.concat([df, dfw], axis=0)
df.reset_index(inplace=True)
df.drop(['index'], axis=1, inplace=True)
df['dateRep'] = pd.to_datetime(df['dateRep'])

# Create Running-total
df.sort_values(by=['countriesAndTerritories', 'dateRep'], inplace=True) # Sort to get cumsum in correct order
df['running_death'] = df.groupby('countriesAndTerritories')['deaths'].cumsum()
df['running_cases'] = df.groupby('countriesAndTerritories')['cases'].cumsum()

# Save the data
joblib.dump(df, os.path.join(dirname, '../data/processed/covid.pkl'))

#SP500 Covid

# SP500 yahoo API.
# min_date =  2019-04-01, max_date = 2020-03-30, period1 = 1554014464, period2 = 1585636864
# The time period is in Linux Epoch for 12:00 AM of that day (closing?)
period1 = df.dateRep.min().strftime('%s')
#period2 = df.dateRep.max().strftime('%s') # This doesn't work since it seems to not take the latest closing date if we
# were close to a weekend
period2 = date.today().strftime('%s')
sp500_url = 'https://query1.finance.yahoo.com/v7/finance/download/%5EGSPC?period1=' + period1 + '&period2=' + period2 + '&interval=1d&events=history'

r = requests.get(sp500_url)
with open(os.path.join(dirname, '../data/raw/sp500.csv'), 'w') as f:
    f.write(r.text)

sp = pd.read_csv(os.path.join(dirname, '../data/raw/sp500.csv'))
sp.columns = sp.columns.str.lower()

joblib.dump(sp, os.path.join(dirname, '../data/processed/sp500.pkl'))
