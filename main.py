#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import getrandbits
from base64 import urlsafe_b64encode
from datetime import date, datetime, timedelta

import psycopg2
from psycopg2.extras import DictCursor

import pygments
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, get_all_lexers
from pygments.formatters import HtmlFormatter

from flask import Flask, \
		render_template, url_for, flash, \
		request, redirect, Response, abort

from stats import pasteview, pastecount, getstats
import config

app = Flask(__name__)
app.secret_key = config.secret_key
app.config['MAX_CONTENT_LENGTH'] = config.max_content_length


lexers_all = get_all_lexers()
year = date.today().year



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
	return stats

def url_collision(db, route):
	for rule in app.url_map.iter_rules():
		if rule.rule == '/' + route:
			return True
	with db.cursor() as cur: 
		cur.execute("SELECT pasteid FROM pastes WHERE pasteid = %s;", (route,))
		if cur.fetchone():
			return True
	return False

def db_newpaste(db, opt, stats):
	date = datetime.utcnow()
	date += timedelta(hours=float(opt['ttl']))
	with db.cursor() as cur:
		cur.execute("""INSERT INTO 
			pastes (pasteid, token, lexer, expiration, burn, 
			paste, size, lines, sloc)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""", \
			(opt['pasteid'], opt['token'], opt['lexer'], \
			date, opt['burn'], opt['paste'], \
			stats['size'], stats['lines'], stats['sloc']))

def db_getpaste(db, pasteid):
	with db.cursor(cursor_factory = DictCursor) as cur:
		cur.execute(("""SELECT * FROM pastes WHERE pasteid=%s;"""), (pasteid,))
		r = cur.fetchone()
	return r


def db_deletepaste(db, pasteid):
	with db.cursor() as cur:
		cur.execute(("""DELETE FROM pastes WHERE pasteid=%s;"""), (pasteid,))

def db_burn(db, pasteid):
	with db.cursor() as cur:
		cur.execute(("""UPDATE pastes SET burn = burn - 1 WHERE pasteid=%s;"""), (pasteid,))

@app.route('/', methods=['GET', 'POST'])
@app.route('/newpaste', methods=['POST']) #only used via html form
def newpaste():
	if request.method == 'POST':
		paste_opt = {}
		for param in config.defaults: #init form parameters with defaults
				paste_opt[param] = config.defaults[param]
		for param in request.form:
			if param in paste_opt:
				paste_opt[param] = request.form[param]
		if paste_opt['paste'] == '':
			return config.empty_paste
		try:
			if not config.paste_limits['ttl_min'] < \
						float(paste_opt['ttl']) < \
						config.paste_limits['ttl_max']:
				return config.invalid_ttl
		except ValueError:
			return config.invalid_ttl
		try:
			if paste_opt['lexer'] == 'auto':
				paste_opt['lexer'] = guess_lexer(paste_opt['paste']).aliases[0]
		except pygments.util.ClassNotFound:
			paste_opt['lexer'] = 'text'
		try:
			if paste_opt['burn'] == '' or paste_opt['burn'] == 0 or paste_opt['burn'] == config.defaults['burn']:
				paste_opt['burn'] = config.defaults['burn']
			elif not config.paste_limits['burn_min'] <= int(paste_opt['burn']) <= config.paste_limits['burn_max']:
				return config.invalid_burn
		except ValueError:
			return config.invalid_burn

		with psycopg2.connect(config.dsn) as db:
			url_len = config.url_len
			paste_opt['pasteid'] = ''
			while url_collision(db, paste_opt['pasteid']):
				for i in range(url_len):
					paste_opt['pasteid'] += base_encode(getrandbits(6))	
				url_len += 1
			
			paste_opt['token'] = \
				urlsafe_b64encode(getrandbits(48).to_bytes(config.token_len, 'little')).decode('utf-8')
			
			stats = paste_stats(paste_opt['paste']) #generate text stats
			
			db_newpaste(db, paste_opt, stats)
			
			pastecount(db) #increment total pastes

			if request.path != '/newpaste': #plaintext reply 
				return "token: " + paste_opt['token'] + " - " + config.domain + url_for('viewraw', pasteid = paste_opt['pasteid']) + "\n"
			
			flash(paste_opt['token'])
		return redirect(paste_opt['pasteid'])
	elif request.method == 'GET':
		return render_template('newpaste.html', \
				lexers_all = lexers_all, lexers_common = config.lexers_common, \
				ttl = config.ttl_options, paste_limits = config.paste_limits, year = year)
	else:
		abort(405)


@app.route('/<pasteid>', methods=['GET', 'DELETE'])
def viewpaste(pasteid):
	if request.method == 'GET':
		direction = 'ltr'
		with psycopg2.connect(config.dsn) as db:
			result = db_getpaste(db, pasteid)
			if not result:
				abort(404)
			if result['burn'] == 0 or result['expiration'] < datetime.utcnow():
				db_deletepaste(db, pasteid)
				abort(404)
			elif result['burn'] > 0:
				db_burn(db, pasteid)
			
			pasteview(db) #count towards total paste views

			if request.args.get('raw') is not None:
				return plain(result['paste'])
			
			if request.args.get('d') is not None:
				direction = 'rtl'
			
			lexer = get_lexer_by_name(result['lexer'])
			formatter = HtmlFormatter(nowrap=True, cssclass='paste')
			paste = highlight(result['paste'], lexer, formatter)

			stats = {'lines': result['lines'],
					'sloc': result['sloc'],
					'size': result['size'],
					'lexer': lexer.name
			}
			del_url = url_for('deletepaste', pasteid=pasteid, token=result['token'])
			return render_template('viewpaste.html', \
				stats=stats, paste=paste.split("\n"), direction=direction, delete=del_url, year=year)
		abort(500)
	elif request.method == 'DELETE':
		with psycopg2.connect(config.dsn) as db:
			result = db_getpaste(db, pasteid)
			if not result:
				return config.msg_err_404, 404
			elif 'token' in request.form and result['token'] == request.form['token']:
				db_deletepaste(db, pasteid)
				return config.msg_paste_deleted, 200
			elif 'token' in request.headers and result['token'] == request.headers.get('token'):
				db_deletepaste(db, pasteid)
				return config.msg_paste_deleted, 200
			else:
				return config.msg_err_401, 401	
	else:
		abort(405)

@app.route('/plain/<pasteid>', methods=['GET', 'DELETE'])
@app.route('/raw/<pasteid>', methods=['GET', 'DELETE'])
def viewraw(pasteid):
	if request.method == 'GET':
		with psycopg2.connect(config.dsn) as db:
			result = db_getpaste(db, pasteid)
			if not result:
				return config.msg_err_404, 404
			if result['burn'] == 0 or result['expiration'] < datetime.utcnow():
				db_deletepaste(db, pasteid)
				return config.msg_err_404, 404
			elif result['burn'] > 0:
				db_burn(db, pasteid)
	
			pasteview(db) #count towards total paste views
			
			return result['paste']

	elif request.method == 'DELETE':
		with psycopg2.connect(config.dsn) as db:
			result = db_getpaste(db, pasteid)
			if not result:
				return config.msg_err_404, 404
			elif 'token' in request.form and result['token'] == request.form['token']:
				db_deletepaste(db, pasteid)
				return config.msg_paste_deleted, 200
			elif 'token' in request.headers and result['token'] == request.headers.get('token'):
				db_deletepaste(db, pasteid)
				return config.msg_paste_deleted, 200
			else:
				return config.msg_err_401, 401
	else:
		return "invalid http method\n"

@app.route('/<pasteid>/<token>', methods=['GET'])
def	deletepaste(pasteid, token):
	with psycopg2.connect(config.dsn) as db:
		result = db_getpaste(db, pasteid)
		if not result:
			abort(404)
		elif result['token'] == token:
		    db_deletepaste(db, pasteid)
		    return render_template('deleted.html')
		else:
			abort(401)
			
@app.route('/about/api')
def aboutapi():
	return render_template('api.html', year=year)

@app.route('/about')
def aboutpage():
	return render_template('about.html', year=year)

@app.route('/stats')
def statspage():
	with psycopg2.connect(config.dsn) as db:
		stats = getstats(db)
		return render_template('stats.html', year=year, stats = stats)


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error():
	return render_template('500.html'), 500

if __name__ == '__main__':
	app.debug = False
	app.run()
