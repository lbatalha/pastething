#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import getrandbits
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import psycopg2
import psycopg2.extras

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

cursor_factory = psycopg2.extras.DictCursor
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
	with db.cursor() as cur:
		cur.execute("""SELECT pasteid FROM pastes WHERE pasteid = %s;""", (route,))
		if cur.fetchone():
			return True
	return False

def db_newpaste(db, opt):
	date = datetime.utcnow()
	date += timedelta(hours=float(opt['ttl']))
	with db.cursor() as cur:
		cur.execute("""INSERT INTO pastes (pasteid, token, lexer, expiration, burn, paste) VALUES (%s, %s, %s, %s, %s, %s);""", (opt['pasteid'], opt['token'], opt['lexer'], date, opt['burn'], opt['paste'])) 
	return True

def db_getpaste(db, pasteid):
	with db.cursor(cursor_factory=cursor_factory) as cur:
		cur.execute(("""SELECT * FROM pastes WHERE pasteid=%s;"""), (pasteid,))
		r = cur.fetchone()
	return r
	
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
			if not config.ttl_min < float(paste_opt['ttl']) < config.ttl_max:
				return config.invalid_ttl
		except ValueError:
			return config.invalid_ttl

		try:
			if paste_opt['lexer'] == 'auto':
				paste_opt['lexer'] = guess_lexer(paste_opt['paste']).aliases[0]
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
			return redirect(paste_opt['pasteid'])
		else:
			db.close()
			return 500
	else:
		return render_template('newpaste.html', lexers_all = lexers_all, lexers_common = config.lexers_common, ttl = config.ttl_options, ttl_max = config.ttl_max, ttl_min = config.ttl_min)

@app.route('/<pasteid>', methods=['GET'])
def viewpaste(pasteid):
	if request.method == 'GET':
		if request.args.get('r') is not None:
				return plain(paste)

		direction = 'ltr'
		if request.args.get('d') is not None:
			direction = 'rtl'
		
		with psycopg2.connect(config.dsn) as db:
			result = db_getpaste(db,pasteid)
			print(result)
			return
			#TODO: store stats in DB
			stats = paste_stats(result['paste'])

			lexer = get_lexer_by_name(result['lexer'])
			formatter = HtmlFormatter(nowrap=True, cssclass='paste')
			paste = highlight(result['paste'], lexer, formatter)
			return render_template('viewpaste.html', stats=stats, paste=paste.split("\n"), direction=direction)
		return 500
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
