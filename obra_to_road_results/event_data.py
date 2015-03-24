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
import time


data_dir = os.path.join(os.path.split(__file__)[0], 'data')

stop_after = 99999

def strip_file_chars(s):
    return s.replace('/', '-').replace('\\', '-').replace(':', ' - ')


def strip_bad_utf8_chars(s):
    return s.replace('&copy;', '(c)').replace('\u2019', "'").replace('\u2014', '-')

def download_all():
    """
    1. iterates through all events from the event.json file
      - downloads and parses event data and outputs to csv
    2. outputs list of events that were downloaded to csv
    """
    
    event_json_filename = os.path.join(data_dir, 'events.json')
    
    with open(event_json_filename) as f:
        all_events = json.loads(f.read())
        
    processed_files = []
    event_data_dir = os.path.join(data_dir, 'event_data')
    if not os.path.exists(event_data_dir):
        os.mkdir(event_data_dir)
        
    for f in os.listdir(event_data_dir):
        race, ext = os.path.splitext(f)
        processed_files.append(strip_bad_utf8_chars(strip_file_chars(race)))
        
    downloaded_events = [['name', 'date', 'discipline', 'city', 'filename', 'event_exists_on_road_results']]
    
    num_processed = 0
    
    for event_url in all_events:
        event_data = all_events[event_url]
        
        event_dt = datetime.strptime(event_data['date'], '%Y-%m-%d')
        race_name = strip_bad_utf8_chars(strip_file_chars(event_data['date'] + '_' + event_data['name']))
        if race_name in processed_files:
            continue
        
        if event_dt.year > 2005:
            downloaded_output_filename, city = download_event(event_url, event_data)
            if downloaded_output_filename:
                downloaded_events.append([event_data['name'],
                                          event_data['date'],
                                          event_data['discipline'],
                                          city,
                                          downloaded_output_filename])
                print(race_name)
            
            time.sleep(1)
            
        else:
            # the pre-2006 event formats are all a crapshoot, no standardization whatsoever
            pass
        
        num_processed += 1
        if num_processed == stop_after:
            break
        
    with open(event_json_filename, 'w') as f:
        f.write(json.dumps(all_events))
        
    with open(os.path.join(data_dir, 'downloaded_events.csv'), 'w',  newline='') as f:
        wrtr = csv.writer(f)
        wrtr.writerows(downloaded_events)
            
        
def download_event(event_url, event_data):
    resp = requests.get(event_url)
    text = resp.text.replace('&copy;', '(c)')
    text = text.replace('\u2019', "'")
    event_hash = hashlib.sha1(text.encode('utf-8')).hexdigest()
    if 'event_data_hash' in event_data and event_data['event_data_hash'] == event_hash:
        return False, None
        
    event_data['event_data_hash'] = event_hash
    event_soup = BeautifulSoup(text)
    
    event_info = event_soup.find(class_='row event_info')
    event_city = event_info.contents[0].strip()
    
    output_rows = [['Place', 'Name', 'Team']]
    
    for item in event_soup.find_all(['h3', 'table']):
        if item.name == 'h3':
            output_rows.append([])
            output_rows.append([item.string])
        elif item.has_attr('class') and 'event_races' not in item['class']:
            time_pos = False
            
            for th in item.find_all('th'):
                if th.has_attr('class') and 'time' in th['class']:
                    time_pos = True
                    if len(output_rows[0]) == 3:
                        output_rows[0].append('Time')
                
            for tr in item.find_all('tr'):
                row = ['', '' ,'']
                if time_pos:
                    row.append('')
                    
                for td in tr.find_all('td'):
                    try:
                        if td.has_attr('class'):
                            if 'place' in td['class']:
                                row[0] = td.string
                            elif 'name' in td['class']:
                                row[1] = td.string
                            elif 'team_name' in td['class']:
                                row[2] = td.string
                            elif 'time' in td['class']:
                                row[3] = td.string
                    except Exception as e:
                        print(td)
                        print(row)
                        raise e
                        
                if len(tr.find_all('td')) > 0:
                    output_rows.append(row)
                     
    event_data_dir = os.path.join(data_dir, 'event_data')
    if not os.path.exists(event_data_dir):
        os.mkdir(event_data_dir)
        
    output_filename = strip_bad_utf8_chars(strip_file_chars(event_data['date'] + '_' + event_data['name'])) + '.csv'
    output_path = os.path.join(event_data_dir, output_filename)
        
    if len(output_rows) < 2:
        return False, None
    
    with open(output_path, 'w',  newline='') as f:
        wrtr = csv.writer(f)
        wrtr.writerows(output_rows) 
    
    return output_filename, event_city
    