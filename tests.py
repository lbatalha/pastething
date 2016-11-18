import main
import config
import stats
import gc

from random import getrandbits

def test_plainresponse():
	assert main.plain('test').headers['Content-Type'] == 'text/plain; charset=utf-8'


