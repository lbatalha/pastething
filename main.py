#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import getrandbits
from base64 import urlsafe_b64encode

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import pygments
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from flask import Flask
from flask import render_template, url_for, flash
from flask import request, redirect, Response, abort

import config

app = Flask(__name__)
app.secret_key = config.secret_key
app.config['MAX_CONTENT_LENGTH'] = config.max_content_length

def base_encode(num):
	if not num:
		return config.url_alph[0]
	result = ''
	while num:
		num, rem = divmod(num, config.base)
		result = result.join(config.url_alph[rem])
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
	stats['lexer'] = 'python'
	return stats

def url_collision(route):
	for rule in app.url_map.iter_rules():
		print(rule.rule)
		if rule.rule == '/' + route:
			return True
	return False

@app.route('/', methods=['GET', 'POST'])
def newpaste():
	print(url_collision('paste'))
	if request.method == 'POST':
		paste_opt = {}
		for param in config.defaults:
				paste_opt[param] = config.defaults[param]
		for param in request.form:
			if param in paste_opt:
				paste_opt[param] = request.form[param]
		if paste_opt['paste'] == '':
			return config.empty_paste

		try:
			if not config.ttl_min < int(paste_opt['ttl']) < config.ttl_max:
				return config.invalid_ttl
		except ValueError:
			return config.invalid_ttl

		print(paste_opt['ttl'])
		print(paste_opt['paste'])
		print(paste_opt['lexer'])

		collision = True
		while collision:
			url = ''
			for i in range(config.url_len):
				url += base_encode(getrandbits(6))
			collision = None
			#url_len += 1
			##placeholder for collision check
		print(url)
		flash(urlsafe_b64encode(getrandbits(48).to_bytes(config.token_len, 'little')).decode('utf-8'))
		return redirect(url_for('viewpaste'))
	return render_template('newpaste.html')

@app.route('/paste', methods=['GET'])
def viewpaste():
	if request.method == 'GET':
		with open('main.py', 'r') as fp:
			paste = fp.read()
			fp.close()

		stats = paste_stats(paste)

		if request.args.get('r') is not None:
				return plain(paste)

		direction = 'ltr'
		if request.args.get('d') is not None:
			direction = 'rtl'

		text = paste
		try:
			lexer = get_lexer_by_name('python')
			formatter = HtmlFormatter(nowrap=True, cssclass='paste')
			paste = highlight(paste, lexer, formatter)
		except pygments.util.ClassNotFound:
			paste = text

		return render_template('viewpaste.html', stats=stats, paste=paste.split("\n"), direction=direction)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
