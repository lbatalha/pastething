import main
import config
import stats
import gc

from random import getrandbits

def test_urlgen():
	for i in range(256):
		assert main.base_encode(getrandbits(config.url_alph_bits)) in config.url_alph

def test_plainresponse():
	assert main.plain('test').headers['Content-Type'] == 'text/plain; charset=utf-8'


