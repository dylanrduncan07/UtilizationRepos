import requests
import pandas as pd
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import os

#Load environment variables
load_dotenv()   

#Pull API Keys from ENV
XK_token = os.getenv('XK_API_KEY')
SM_token = os.getenv('SM_API_KEY')

# Define function to pull API from XK
def fetch_XK(date, XKToken):
    url = f"https://us-central1-xandar-kardian-production.cloudfunctions.net/api/building/occupancy/peak/daily/total?date={date}"
    headers = {
        "Authorization": f"Basic {XKToken}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df.rename(columns={'buildingId': 'Building ID', 'DATE': 'Date', 'Max_Occupancy': 'Max Occupancy'})
    return None

# Define function to fetch data from Smarking API
def fetch_Smarking(location_id, date, SMToken):
    url = f'https://my.smarking.net/api/ds/v3/garages/{location_id}/past/occupancy/from/{date}T05:00:00/19/1h'
    headers = {
        "Authorization": f"Bearer {SMToken}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'value' in data and data['value']:  # Check if 'value' exists and is not empty
            max_value = max(data['value'][0]['value'])
            return {'Building ID': location_id, 'Date': date, 'Max Occupancy': max_value}
    return None

#Filters out weekends 
def is_weekday(date):
    return date.weekday() < 5

#Set Date
vdate = date.today() - timedelta(days = 1)

#Initialize data list
data_list = []

#Initialize data map based on Building ID
id_mapping = {
    '8XhiXuBsPQYlteZlTH8b' : '8301',
    'LeKka3BR93h6ye8K0Da1' : '48201',
    'SCzEUw9HvTL4ICdUPwOf' : '8401',
    'YbsoSfHgduDXf6C9PqvO' : '24901',
    's1LHCkw20XTYVHzV9LuR' : '7001',
    'AMf3W2qg1f8YSZbdGq5n' : '1601',
    'T84Q2oYO96fLVLFjMdNm' : '2501',
    'o33kcembZ7LCuD6O5xfV' : '13601',
    'qyUNEuvTAGBdIGCKWcY8' : '15801',
    '200600' : '10901',
    '455515' : '10601',
    '695676' : '10801',
    '487841' : '13401',
    '450100' : '35001',
    '489363' : '7601',
    '200932' : '44101',
    '738098' : '17001',
    '842334' : '48101',
    '374265' : '48301',
    '844076' : '13901'
}
#Check if yesterday was weekday
if is_weekday(vdate):
    #format date for XK
    date_XK = vdate.strftime('%Y%m%d')
    XK_data = fetch_XK(date_XK, XK_token)
    if XK_data is not None:
            data_list.append(XK_data)
    for location_id in range(1, 12):
         sm_data = fetch_Smarking(os.getenv(f'LocationID{location_id}'), vdate, SM_token)
         if sm_data is not None:
              data_list.append(pd.DataFrame([sm_data]))

#concat dataframes
daily_data = pd.concat(data_list, ignore_index=True)

#Set Building ID's to JDE IDs
daily_data['Building ID'] = daily_data['Building ID'].map(id_mapping)

#pull existing file 
existing_df = pd.read_excel('Utilization_Data.xlsx')

#update existing file
updated_df = pd.concat([existing_df, daily_data], axis=0, ignore_index=True)

#set consistent date type
updated_df['Date'] = pd.to_datetime(updated_df['Date']).dt.date
updated_df['Building ID'] = pd.to_numeric(updated_df['Building ID'])

#Update excel file
updated_df.to_excel('Utilization_Data.xlsx', index=False)

print('File updated successfully')







