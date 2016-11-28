import main
import config
import stats
import gc

import requests
from random import getrandbits

url = "http://localhost:5000/"

def test_plainresponse():
	assert main.plain('test').headers['Content-Type'] == 'text/plain; charset=utf-8'

def test_postlimits():
	#Missing paste body test
	params = {'paste': '', 'burn': 1, 'ttl': 1.0}
	r = requests.post(url, data=params)
	assert r.status_code != 200
	params['paste'] = 'test'

	#burn count too high test
	params['burn'] = config.paste_limits['burn_max'] + 1
	r = requests.post(url, data=params)
	assert r.status_code != 200
	params['burn'] = config.paste_limits['burn_max'] - 1

	#ttl too high test
	params['ttl'] = config.paste_limits['ttl_max'] + 0.1
	r = requests.post(url, data=params)
	assert r.status_code != 200
	params['ttl'] = config.paste_limits['ttl_max'] - 0.1

	#burn too low test
	params['burn'] = config.paste_limits['burn_min'] - 1
	r = requests.post(url, data=params)
	assert r.status_code != 200
	params['burn'] = config.paste_limits['burn_min']

	#ttl too low test
	params['ttl'] = config.paste_limits['ttl_min']
	r = requests.post(url, data=params)
	assert r.status_code != 200

