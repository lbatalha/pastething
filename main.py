#!/usr/bin/env python3

import random
from base64 import urlsafe_b64encode

import textwrap
#------------------------------------------------------------------------------------------------------------
import pygments
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from flask import Flask
from flask import render_template, url_for, flash
from flask import request, redirect, abort

app = Flask(__name__)
app.secret_key = 'some_secret'


rng = random.SystemRandom()
lexer = 'txt'
ttl = 60
url_len = 1
url_alph = tuple("23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz")
base = len(url_alph)

def base_encode(num):
	if not num:
		return url_alph[0]
	result = ''
	while num:
		num, rem = divmod(num, base)
		result = result.join(url_alph[rem])
	return result

@app.route('/', methods=['GET', 'POST'])
def newpaste():
	if request.method == 'POST':

		paste = None
		if 'paste' in request.form and request.form['paste']:
			paste = request.form['paste']
		else:
			return "pls, actually paste something k?\n"
		if request.form['lexer']:
			lexer = request.form['lexer']
		if request.form['ttl']:
			ttl = int(request.form['ttl'])
		
		print(ttl)
		print(lexer)
		print(paste)

		collision = True
		while collision:
			url = ''
			for i in range(url_len):
				url += base_encode(rng.getrandbits(6))
			collision = None
			#url_len += 1
			##placeholder for collision check
		print(url)
		flash(urlsafe_b64encode(rng.getrandbits(48).to_bytes(6, 'little')))
		return redirect(url_for('viewpaste'))
	return render_template('newpaste.html')

@app.route('/paste', methods=['GET'])
def viewpaste():
	if request.method == 'GET':
		with open('main.py', 'r') as fp:
			paste = fp.read()
			fp.close()

		direction = 'ltr'
		if request.args.get('d') is not None:
			direction = 'rtl'
		print(request.args.get('d'))

		wrap = False
		if request.args.get('w') is not None:
			paste = '\n'.join(textwrap.wrap(paste, replace_whitespace=False, width=80))
		print(request.args.get('w'))

		text = ''

		
		try:
			lexer = get_lexer_by_name('python')
			formatter = HtmlFormatter(linenos=True, cssclass='paste')
			paste = highlight(paste, lexer, formatter)
		except pygments.util.ClassNotFound:
			paste = text
		
		return render_template('viewpaste.html', paste=paste, direction=direction)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
