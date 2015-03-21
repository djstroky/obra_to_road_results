"""
A bunch of scripts to download a list of OBRA events
"""
from bs4 import BeautifulSoup
from datetime import date, datetime

import json
import os
import requests
import time


def download():
	"""download links to all event by year and discipline"""

	today = date.today()
	
	url_fmt_pre_2006 = 'http://www.obra.org/results/{0}/index.html'
	base_url_2006_to_present = 'http://obra.org/results/{0}/{1}'
	
	data_dir = os.path.join(os.path.split(__file__)[0], 'data')
	event_json_filename = os.path.join(data_dir, 'events.json')
	if not os.path.exists(data_dir):
		os.makedirs(data_dir)
		
	if os.path.exists(event_json_filename):
		event_file = open(event_json_filename)
		all_race_data = json.loads(event_file.read())
		event_file.close()
	else:
		all_race_data = dict()
	
	for year in range(2006, today.year + 1): 
		if year < 2006:
			# pre-2006 result format
			
			print(year)
			
			result_list_url = url_fmt_pre_2006.format(year)
			parse_pre_2006_list(year, requests.get(result_list_url), all_race_data)
			
			time.sleep(0.5)
			
		else:
			# 2006-present result format

			for discipline in ['criterium', 'road', 'time_trial']:

				print(year, discipline)

				result_list_url = base_url_2006_to_present.format(year, discipline)
				parse_2006_to_present_list(year, discipline, requests.get(result_list_url), all_race_data)

				time.sleep(0.5)	
	
	event_file = open(event_json_filename, 'w')
	event_file.write(json.dumps(all_race_data))
	event_file.close()
	

def parse_2006_to_present_list(year, discipline, resp, all_race_data):
	"""parse the response from a request for 2006-present results
	
	Args:
		year (int): the year
		discipline (string): type of race
        resp (requests response): The result list response
        all_race_data (dict): The dictionary of all race results"""
	
	text = resp.text.replace('&copy;', '(c)')

	# new OBRA website has too many </tr> tags, use html5lib to take care of that
	result_soup = BeautifulSoup(text, 'html5lib')
	
	# only targeting main section.  Weekly Series are not important IMHO
	target_section = result_soup.find(class_='col-sm-6')
	
	last_multi_day_name = 'Unknown Multi-day Race'
	
	for race_tr in target_section.find_all('tr'):
		tds = race_tr.find_all('td')
		if len(tds) < 2:
			# new year, likely a single row with a single td saying "None"
			continue
		
		if tds[0].string.find('-') > -1:
			# multi-day GC, capture name, continue to next
			last_multi_day_name = tds[1].a.string
			continue
		
		race_date_str = tds[0].string.strip()
		race_date_dt = datetime.strptime(race_date_str, '%m/%d')
		race_date_dt = datetime(year, race_date_dt.month, race_date_dt.day)
		race_link = tds[1].a['href']
		race_link = 'http://obra.org{0}'.format(race_link)
		race_name = tds[1].a.string
		
		if race_tr.has_attr('class') and 'multi-day-event-child' in race_tr['class']:
			if race_name.find(last_multi_day_name) == -1:
				race_name = last_multi_day_name + ' - ' + race_name
		
		if race_link not in all_race_data:
			all_race_data[race_link] = dict(date=race_date_dt.strftime('%Y-%m-%d'),
											name=race_name,
											discipline=discipline)


def parse_pre_2006_list(year, resp, all_race_data):
	"""parse the response from a request for pre-2006 results
	The results are not standardized, so this script probably won't find everything properly.
	Some manual editing of the event.json file will likely be required.
	
	Args:
		year (int): the year
		resp (requests response): The result list response
        all_race_data (dict): The dictionary of all race results"""
	
	text = resp.text.replace('&copy;', '(c)')

	result_soup = BeautifulSoup(text, 'html5lib')
	pre_results = result_soup.find('pre') # first table should contain pre tag of results
	
	last_date = None
	
	race_link_base_url = 'http://obra.org/results/{0}/{1}'
	
	for item in pre_results.contents:
		if type(item).__name__ == 'NavigableString':
			if item.find('-') > -1:
				pass
			else:		
				race_date_str = item.strip()
				try:
					race_date_dt = datetime.strptime(race_date_str, '%m/%d')
					last_date = datetime(year, race_date_dt.month, race_date_dt.day)
				except:
					pass
		else:
			race_link = race_link_base_url.format(year, item['href'])
			
			if race_link not in all_race_data:
				race_name = item.string
				
				race_type = 'unknown'
				if race_name.lower().find('trial') > -1 or\
					race_name.lower().find(' tt') > -1:
					race_type = 'time_trial'
				elif race_name.lower().find('criterium') > -1:
					race_type = 'criterium'
				elif race_name.lower().find('road') > -1 or\
					race_name.lower().find(' rr') > -1:
					race_type = 'road'
					
				all_race_data[race_link] = dict(date=last_date.strftime('%Y-%m-%d'),
												name=race_name,
												discipline=race_type)			
	