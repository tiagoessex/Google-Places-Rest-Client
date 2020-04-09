#import logging
import csv
import requests
import json

import time

'''
logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
'''


def dataStruct():
	result = {}
	result['latitude'] = None
	result['longitude'] = None
	result['name'] = None
	result['place_id'] = None
	result['open_now'] = None
	result['global_code'] = None
	result['rating'] = None
	result['address'] = None
	result['types'] = None
	return result

def getAllPlaces(key = None, latitude = None, longitude = None, radius = 500, type=None, total = 20, keywords = [], token = None):

	if token:
		url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={}&key={}".format(token, key)
		time.sleep(2)	# necessary, otherwise INVALID_REQUEST
	else:
		keyword =	('+'.join(keywords)).replace(" ", "")
		#if not type or len(type) == 0:
		#	url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius={}&key={}".format(latitude, longitude, radius, key)
		#else:
		#	url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius={}&type={}&key={}".format(latitude, longitude, radius, type, key)
		url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius={}&type={}&keyword={}&key={}".format(latitude, longitude, radius, type, keyword, key)

	results = requests.get(url)

	results = results.json()
		
	status = results['status']	
	
	if status != 'OK':
		if status == 'ZERO_RESULTS':
			#raise RuntimeError("No Results!")
			return {'status':'ZERO_RESULTS'}
		elif status == 'OVER_QUERY_LIMIT':
			raise RuntimeError("You have exceded your quota!")
		elif status == 'REQUEST_DENIED':
			raise RuntimeError("Invalid key!")
		elif status == 'INVALID_REQUEST':
			raise RuntimeError("Check the parameters or give it some time between APIs calls!")
		elif status == 'NOT_FOUND':
			raise RuntimeError("No place with that id founded!")
		else:
			raise RuntimeError("Unknown Error!")

	all_data = []
	
	if len(results['results']) > 0:
		for result in results['results']:
			data = dataStruct()
			if result.get('geometry') and result.get('geometry').get('location'):
				data["latitude"] = result.get('geometry').get('location').get('lat')
				data["longitude"] = result.get('geometry').get('location').get('lng')	
			data['name'] = result.get("name")
			data['place_id'] = result.get("place_id")
			if result.get('opening_hours'):
				data['open_now'] = result.get('opening_hours').get('open_now')
			if result.get('plus_code'):
				data['global_code'] = result.get('plus_code').get('global_code')
			data['rating'] = result.get("rating")
			data['address'] = result.get("vicinity")
			if result.get('types'):
				tt = []
				for i in result.get('types'):
					tt.append(i)
			data['types'] = tt
			all_data.append(data)
			if total - len(all_data) <= 0:
				break;
	
	temp = total - len(all_data)
	if temp > 0 and results.get('next_page_token'):
		return all_data + getAllPlaces(key, latitude, longitude, radius, type, temp, results.get('next_page_token'))
	else:
		return all_data

