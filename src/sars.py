import joblib
import requests
import pandas as pd

# SARS Dataset
sars = pd.read_csv('data/raw/sars.csv')
sars.columns = sars.columns.str.lower()

# Index(['dateRep', 'day', 'month', 'year', 'cases', 'deaths',
#        'countriesAndTerritories', 'geoId', 'countryterritoryCode',
#        'popData2018', 'running_death', 'running_cases'],
#       dtype='object')
sars.columns = ['dateRep', 'countriesAndTerritories', 'running_cases', 'running_death', 'running_recovered']
sars['day'] = sars['dateRep'].apply(lambda x: int(x[8:10]))
sars['month'] = sars['dateRep'].apply(lambda x: int(x[5:7]))
sars['year'] = sars['dateRep'].apply(lambda x: int(x[0:4]))
sars = sars[['dateRep', 'day', 'month', 'year', 'countriesAndTerritories', 'running_death',
                'running_cases', 'running_recovered']]

sars['dateRep'] = pd.to_datetime(sars['dateRep'])
# Add World
sworld = sars.groupby('dateRep').sum()
dfs = sworld[['running_cases', 'running_death', 'running_recovered']]
dateRep_dt = sworld.index.to_list()
dateRep = [date.strftime('%Y-%m-%d') for date in dateRep_dt]
dfs['dateRep'] = dateRep
dfs['month'] = dfs['dateRep'].apply(lambda x: int(x[5:7]))
dfs['year'] = dfs['dateRep'].apply(lambda x: int(x[0:4]))
dfs['day'] = dfs['dateRep'].apply(lambda x: int(x[8:10]))
dfs['countriesAndTerritories'] = dfs['day'].apply(lambda x: 'World')
dfs['geoId'] = dfs['day'].apply(lambda x: 'World')
dfs['countryterritoryCode'] = dfs['day'].apply(lambda x: 'World')
dfs = dfs[sars.columns]

# Put back World
sars = pd.concat([sars, dfs], axis=0)
sars.reset_index(inplace=True)
sars.drop(['index'], axis=1, inplace=True)
sars['dateRep'] = pd.to_datetime(sars['dateRep'])


joblib.dump(sp_sars, 'data/processed/sp500_sars.pkl')
joblib.dump(sars, 'data/processed/sars.pkl')

# Get S&P500 SARS
period1 = sars.dateRep.min().strftime('%s')
#period2 = df.dateRep.max().strftime('%s') # This doesn't work since it seems to not take the latest closing date if we
# were close to a weekend
period2 = sars.dateRep.max().strftime('%s')
sp500_sars_url = 'https://query1.finance.yahoo.com/v7/finance/download/%5EGSPC?period1=' + period1 + '&period2=' + period2 + '&interval=1d&events=history'

r = requests.get(sp500_sars_url)
with open('data/raw/sp500_sars.csv', 'w') as f:
    f.write(r.text)

sp_sars = pd.read_csv('data/raw/sp500_sars.csv')
sp_sars.columns = sp_sars.columns.str.lower()