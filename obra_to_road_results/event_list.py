"""
A bunch of scripts to download a list of OBRA events
"""
from bs4 import BeautifulSoup
from datetime import date, datetime

import requests
import time


FMT_2006_TO_PRESENT = 'http://obra.org/results/{0}/{1}'


def download():
	"""download links to all event by year and discipline"""

	today = date.today()
	
	all_race_data = []
	
	for year in range(2014, today.year): #range(2001, today.year): 
		if year < 2006:
			#pre-2006 result format
			pass
		else:
			#2006-present result format

			for discipline in ['road', 'time_trial']:  #['criterium', 'road', 'time_trial']:

				print(year, discipline)

				result_list_url = FMT_2006_TO_PRESENT.format(year, discipline)
				all_race_data += parse_2006_to_present_list(year, discipline, requests.get(result_list_url))

				time.sleep(0.5)

	print(all_race_data)

def parse_2006_to_present_list(year, discipline, resp):
	"""parese the response
	
	Args:
		year (int): the year
		discipline (string): type of race
        resp (requests response): The result list response
        
	Returns:
		"""
	
	text = resp.text.replace('&copy;', '(c)')

	result_soup = BeautifulSoup(text)

	#only targeting main section.  Weekly Series are not important IMHO
	target_section = result_soup.find(class_='col-sm-6')
	
	races = []
	
	for race in target_section.find_all('tr'):
		tds = race.find_all('td')
		if tds[0].string.find('-') > -1:
			#multi-day GC, continue to next
			continue
		
		race_date_str = tds[0].string.strip()
		race_date_dt = datetime.strptime(race_date_str, '%m/%d')
		race_date_dt = datetime(year, race_date_dt.month, race_date_dt.day)
		races.append(dict(date=race_date_dt.strftime('%Y-%m-%d'),
						  link=tds[1].a.href,
						  name=tds[1].string,
						  discipline=discipline))
	
	return races
