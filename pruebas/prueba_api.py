import requests
import json

url = 'https://edc.dgfi.tum.de/api/v1/'

args = {}
''' required options '''
args['username'] = 'username'
args['password'] = 'password'
args['action'] = 'data-download'
args['id'] = '1300505'
args['data_type'] = 'NPT'
# available data types: 'NPT','FRD','LTT','CPF','NP','FR','CPF_v2','NPT_v2','FRD_v2'

''' send request as method POST '''
response = requests.post(url, data=args)

if response.status_code == 200:
	''' convert json string in python list '''
	data = json.loads(response.text)
	for record in data:
		print (record)
else:
	print (response.status_code)
	print (response.text)