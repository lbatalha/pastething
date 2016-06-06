#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import getrandbits
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import psycopg2

import pygments
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, get_all_lexers
from pygments.formatters import HtmlFormatter

from flask import Flask, \
		render_template, url_for, flash, \
		request, redirect, Response, abort

import config

app = Flask(__name__)
app.secret_key = config.secret_key
app.config['MAX_CONTENT_LENGTH'] = config.max_content_length

lexers_all = get_all_lexers()

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

def url_collision(db, route):
	for rule in app.url_map.iter_rules():
		print(rule.rule)
		if rule.rule == '/' + route:
			return True
	cur = db.cursor()
	cur.execute("""SELECT DISTINCT pasteid FROM pastes WHERE pasteid = %s;""", (route))
	if cur.fetchone():
		return True
	return False

def db_newpaste(db, opt):
	date = datetime.utcnow()
	date += timedelta(hours=int(opt['ttl']))
	cur = db.cursor()
	#try:
	cur.execute("""INSERT INTO pastes (pasteid, token, lexer, expiration, burn, paste) VALUES (%s, %s, %s, %s, %s, %s);""", (opt['pasteid'], opt['token'], opt['lexer'], date, opt['burn'], opt['paste'])) 
	db.commit()
	return True
	#except:
	#cur.rollback()
	#return False

@app.route('/', methods=['GET', 'POST'])
def newpaste():
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
			if not config.ttl_min <= int(paste_opt['ttl']) <= config.ttl_max:
				return config.invalid_ttl
		except ValueError:
			return config.invalid_ttl

		try:
			if paste_opt['lexer'] == 'auto':
				paste_opt['lexer'] = guess_lexer(paste_opt['paste']).name
		except pygments.util.ClassNotFound:
			paste_opt['lexer'] = 'txt'
		
		try:
			if paste_opt['burn'] == '':
				paste_opt['burn'] = config.defaults['burn']
			elif not config.burn_min <= int(paste_opt['burn']) <= config.burn_max:
				return config.invalid_burn
		except ValueError:
			return config.invalid_burn

		db = psycopg2.connect(config.dsn)

		url_len = config.url_len
		paste_opt['pasteid'] = ''
		while url_collision(db, paste_opt['pasteid']):
			for i in range(url_len):
				paste_opt['pasteid'] += base_encode(getrandbits(6))
			url_len += 1
		
		paste_opt['token'] = urlsafe_b64encode(getrandbits(48).to_bytes(config.token_len, 'little')).decode('utf-8')
				
		if db_newpaste(db, paste_opt):
			db.close()
			return redirect(url_for('viewpaste'))
		else:
			db.close()
			return 500
	else:
		return render_template('newpaste.html', lexers_all = lexers_all, lexers_common = config.lexers_common, ttl = config.ttl_options, ttl_max = config.ttl_max, ttl_min = config.ttl_min)

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

@app.route('/about/api')
def aboutapi():
	return render_template('api.html')

@app.route('/about')
def aboutpage():
	return render_template('about.html')

@app.route('/stats')
def statspage():
	return render_template('stats.html')

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
