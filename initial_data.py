import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve API Tokens
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

# Filter out weekends
def is_weekday(date):
    return date.weekday() < 5

# Set start & end dates
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 5, 22)

# Initialize empty list to store data
data_list = []

# Initiliaze data map for BuildingID

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


# Iterate over dates
current_date = start_date
while current_date <= end_date:
    if is_weekday(current_date):
        formatted_date = current_date.strftime("%Y%m%d")
        XK_data = fetch_XK(formatted_date, XK_token)
        if XK_data is not None:
            data_list.append(XK_data)
        for location_id in range(1, 11):
            sm_data = fetch_Smarking(os.getenv(f'LocationID{location_id}'), current_date, SM_token)
            if sm_data is not None:
                data_list.append(pd.DataFrame([sm_data]))
    current_date += timedelta(days=1)

# Concatenate dataframes
all_data = pd.concat(data_list, ignore_index=True)

# Set Building ID's to JD Edwards IDs
all_data['Building ID'] = all_data['Building ID'].map(id_mapping)

# Set consistent date column
all_data['Date'] = pd.to_datetime(all_data['Date']).dt.date


# Save to Excel
all_data.to_excel('Utilization_Data.xlsx', index=False)
print('Excel File saved successfully')
