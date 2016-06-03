#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from flask import request, redirect, Response, abort

app = Flask(__name__)
app.secret_key = 'some_secret'

rng = random.SystemRandom()

plain_useragents = ('curl','wget', None)
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

def plain(text):
	resp = Response(text)
	resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
	return resp

def paste_stats(text):
	stats = {}
	stats['lines'] = len(text.split('\n'))
	stats['sloc'] = stats['lines'] - len(text.split('\n\n'))
	stats['size'] = len(text.encode('utf-8'))
	return stats


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

		stats = paste_stats(paste)

		user_agent = request.user_agent.browser
		for ua in plain_useragents:
			if user_agent == ua:
				return plain(paste)
		if request.args.get('plain') is not None:
				return plain(paste)

		direction = 'ltr'
		if request.args.get('d') is not None:
			direction = 'rtl'

		wrap = False
		if request.args.get('w') is not None:
			wrap = True

		text = paste
		try:
			lexer = get_lexer_by_name('python')
			formatter = HtmlFormatter(linespans='linespan', linenos=False, cssclass='paste')
			paste = highlight(paste, lexer, formatter)
		except pygments.util.ClassNotFound:
			paste = text
		
		return render_template('viewpaste.html', stats=stats, paste=paste, direction=direction)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
