import requests
import json

if '__main__' in __name__:
	with open('keys.json') as keys_file:
		keys = json.load(keys_file)
		keys_file.close()

	url = 'http://developer.echonest.com/api/v4/artist/hotttnesss?api_key=' + \
		  keys['API_KEY'] + \
		  '&name=lady+gaga&format=json'
	r = requests.get(url)
	print r.response
	


