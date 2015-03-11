"""
Some scripts to download, parse and transform individual race results into 
format readable by road-results
"""
from bs4 import BeautifulSoup
from datetime import datetime

import csv
import hashlib
import json
import os
import requests
import sys


def download_all():
    """
    1. iterates through all events from the event.json file
      - downloads and parses event data and outputs to csv
    2. outputs list of events that were downloaded to csv
    """
    
    data_dir = os.path.join(os.path.split(__file__)[0], 'data')
    event_json_filename = os.path.join(data_dir, 'events.json')
    
    with open(event_json_filename) as f:
        all_events = json.loads(f.read())
        
    downloaded_events = ['name', 'date', 'discipline', 'city', 'filename']
    
    for event_url in all_events:
        event_data = all_events[event_url]
        event_dt = datetime.strptime(event_data['date'], '%Y-%m-%d')
        
        if event_dt.year > 2005:
            downloaded_output_filename, city = download_event(event_url, event_data)
            if downloaded_output_filename:
                downloaded_events.append([event_data['name'],
                                          event_data['date'],
                                          event_data['discipline'],
                                          city,
                                          downloaded_output_filename])
        else:
            # the pre-2006 event formats are all a crapshoot, no standardization whatsoever
            pass
        
    with open(event_json_filename, 'w') as f:
        f.write(json.dumps(all_events))
        
    with open(os.path.join(data_dir, 'downloaded_events.csv'), 'w') as f:
        wrtr = csv.writer(f)
        wrtr.writerows(downloaded_events)
            
        
def download_event(event_url, event_data):
    resp = requests.get(event_url)
    text = resp.text.replace('&copy;', '(c)')
    event_hash = hashlib.sha1(text.encode('utf-8')).hexdigest()
    if 'event_data_hash' in event_data and event_data['event_data_hash'] == event_hash:
        return False
        
    event_data['event_data_hash'] = event_hash
    event_soup = BeautifulSoup(text)
    
    sys.exit()
    