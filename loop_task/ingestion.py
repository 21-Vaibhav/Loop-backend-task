import pandas as pd
from sqlalchemy import create_engine

# Database connection
engine = create_engine('postgresql://postgres:password@localhost/loopaitask')

# Load store_status CSV
store_status_df = pd.read_csv('store_status.csv')
store_status_df.to_sql('store_status', engine, if_exists='replace', index=False)

# Load store_hours CSV
store_hours_df = pd.read_csv('store_hours.csv')
store_hours_df.to_sql('store_hours', engine, if_exists='replace', index=False)

# Load store_timezones CSV
store_timezones_df = pd.read_csv('store_timezones.csv')
store_timezones_df.to_sql('store_timezones', engine, if_exists='replace', index=False)
