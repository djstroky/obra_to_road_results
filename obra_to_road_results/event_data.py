from datetime import datetime
import hashlib
import json
import os
import requests


def download_all():
    data_dir = os.path.join(os.path.split(__file__)[0], 'data')
    event_json_filename = os.path.join(data_dir, 'events.json')
    
    with open(event_json_filename) as f:
        all_events = json.loads(f.read())
    
    for event_url in all_events:
        event_data = all_events[event_url]
        event_dt = datetime.strptime(event_data['date'], '%Y-%m-%d')
        
        if event_dt.year > 2005:
            download_event(event_url, event_data)
        else:
            # the pre-2006 event formats are all a crapshoot, no standardization whatsoever
            pass
        
    with open(event_json_filename, 'w') as f:
        f.write(json.dumps(all_events))
        
        
def download_event(event_url, event_data):
    resp = requests.get(event_url)
    event_hash = hashlib.sha1(resp.text.encode('utf-8')).hexdigest()
    if 'event_data_hash' in event_data and event_data['event_data_hash'] == event_hash:
        return False
        
    event_data['event_data_hash'] = event_hash
    