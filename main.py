#!/usr/bin/env python3

from random import getrandbits, choice
from base64 import urlsafe_b64encode
from datetime import date, datetime, timedelta
from contextlib import contextmanager

from psycopg2.extras import DictCursor
from psycopg2.pool import SimpleConnectionPool

import pygments
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, get_all_lexers
from pygments.formatters import HtmlFormatter

from flask import Flask, \
		render_template, url_for, flash, \
		request, redirect, Response, abort, \
		get_flashed_messages, make_response

from stats import pasteview, pastecount, getstats

import config

app = Flask(__name__)
app.secret_key = config.secret_key
app.config['MAX_CONTENT_LENGTH'] = config.max_content_length
app.jinja_env.globals['year'] = date.today().year #local server date

#Setup connection pool
connpool = SimpleConnectionPool(config.connpool_min, config.connpool_max, config.dsn)

@contextmanager
def getcursor(cursor_factory=None):
	con = connpool.getconn()
	try:
		if cursor_factory:
			yield con.cursor(cursor_factory=cursor_factory)
		else:
			yield con.cursor()
		con.commit()
	finally:
		connpool.putconn(con)

def plain(text):
	resp = Response(text)
	resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
	return resp

def set_cache_control(resp, max_age=69):
	resp.cache_control.public = True
	resp.cache_control.max_age = int(max_age)
	return resp

def paste_stats(text):
	stats = {}
	stats['lines'] = len(text.split('\n'))
	stats['sloc'] = stats['lines']
	for line in text.split('\n'):
		if not line.strip():
			stats['sloc'] -= 1
	stats['size'] = len(text.encode('utf-8'))
	return stats

def url_collision(cursor, route):
	for rule in app.url_map.iter_rules():
		if rule.rule == '/' + route:
			return True
	with cursor as cur:
		cur.execute("SELECT pasteid FROM pastes WHERE pasteid = %s;", (route,))
		if cur.fetchone():
			return True
	return False

def db_newpaste(cursor, opt, stats):
	date = datetime.utcnow()
	date += timedelta(hours=float(opt['ttl']))
	with cursor as cur:
		cur.execute("""INSERT INTO
			pastes (pasteid, token, lexer, expiration, burn,
			paste, paste_lexed, size, lines, sloc)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", \
			(opt['pasteid'], opt['token'], opt['lexer'], \
			date, opt['burn'], opt['paste'], opt['paste_lexed'], \
			stats['size'], stats['lines'], stats['sloc']))

def db_getpaste(cursor, pasteid):
	with cursor as cur:
		cur.execute(("""SELECT * FROM pastes WHERE pasteid = %s;"""), (pasteid,))
	return cur.fetchone()


def db_deletepaste(cursor, pasteid):
	with cursor as cur:
		cur.execute(("""DELETE FROM pastes WHERE pasteid = %s;"""), (pasteid,))

def db_burn(cursor, pasteid):
	with cursor as cur:
		cur.execute(("""UPDATE pastes SET burn = burn - 1 WHERE pasteid = %s;"""), (pasteid,))

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
			return config.msg_empty_paste, 400
		try:
			if not config.paste_limits['ttl_min'] < \
						float(paste_opt['ttl']) < \
						config.paste_limits['ttl_max']:
				return config.msg_invalid_ttl, 400
		except ValueError:
			return config.msg_invalid_ttl, 400
		lexer = ""
		try:
			if paste_opt['lexer'] == 'auto':
				lexer = guess_lexer(paste_opt['paste'])
				paste_opt['lexer'] = lexer.aliases[0]
			else:
				lexer = get_lexer_by_name(paste_opt['lexer'])
		except pygments.util.ClassNotFound:
			paste_opt['lexer'] = 'text'
			lexer = get_lexer_by_name(paste_opt['lexer'])

		formatter = HtmlFormatter(nowrap=True, cssclass='paste')
		paste_opt['paste_lexed'] = highlight(paste_opt['paste'], lexer, formatter)

		try:
			if paste_opt['burn'] == '' or paste_opt['burn'] == 0 or paste_opt['burn'] == config.defaults['burn']:
				paste_opt['burn'] = config.defaults['burn']
			elif not config.paste_limits['burn_min'] <= int(paste_opt['burn']) <= config.paste_limits['burn_max']:
				return config.msg_invalid_burn, 400
		except ValueError:
			return config.msg_invalid_burn, 400

		url_len = config.url_len
		paste_opt['pasteid'] = ''
		while url_collision(getcursor(), paste_opt['pasteid']):
			for _ in range(url_len):
				paste_opt['pasteid'] += choice(config.url_alph)
			url_len += 1

		paste_opt['token'] = \
			urlsafe_b64encode((getrandbits(config.token_len * 8)) \
				.to_bytes(config.token_len, 'little')).decode('utf-8')

		stats = paste_stats(paste_opt['paste']) #generate text stats

		db_newpaste(getcursor(), paste_opt, stats)

		pastecount(getcursor()) #increment total pastes

		if request.path != '/newpaste': #plaintext reply
			if paste_opt['raw'] == 'true':
				reptype = 'viewraw'
			else:
				reptype = 'viewpaste'
			return config.domain + url_for(reptype, pasteid=paste_opt['pasteid']) + \
					" | " + paste_opt['token'] + "\n"

		flash(paste_opt['token'])
		return redirect(paste_opt['pasteid'])
	elif request.method == 'GET':
		lexers_all = sorted(get_all_lexers())
		return set_cache_control(make_response(render_template('newpaste.html', \
				lexers_all=lexers_all, lexers_common=config.lexers_common, \
				ttl=config.ttl_options, paste_limits=config.paste_limits)), config.nonpaste_max_age)

@app.route('/<pasteid>', methods=['GET', 'DELETE'])
def viewpaste(pasteid):
	if request.method == 'GET':
		direction = 'ltr'
		result = db_getpaste(getcursor(cursor_factory=DictCursor), pasteid)
		if not result:
			abort(404)
		if result['burn'] == 0 or result['expiration'] < datetime.utcnow():
			db_deletepaste(getcursor(), pasteid)
			abort(404)
		elif result['burn'] > 0:
			db_burn(getcursor(), pasteid)

		pasteview(getcursor()) #count towards total paste views

		if request.args.get('raw') is not None:
			return set_cache_control(plain(result['paste']), config.paste_max_age)

		if request.args.get('d') is not None:
			direction = 'rtl'

		stats = {'lines': result['lines'],
				'sloc': result['sloc'],
				'size': result['size'],
				'lexer': result['lexer']
		}
		messages = get_flashed_messages()
		if messages:
			token = messages[0]
		else:
			token = ''

		del_url = url_for('deletepaste', pasteid=pasteid, token=token)
		resp = make_response(render_template('viewpaste.html', \
			stats=stats, paste=result['paste_lexed'].split("\n"), direction=direction, delete=del_url))
		return set_cache_control(resp, config.paste_max_age)

	elif request.method == 'DELETE':
		result = db_getpaste(getcursor(cursor_factory=DictCursor), pasteid)
		if not result:
			return config.msg_err_404, 404
		elif 'token' in request.form and result['token'] == request.form['token']:
			db_deletepaste(getcursor(), pasteid)
			return config.msg_paste_deleted, 200
		elif 'token' in request.headers and result['token'] == request.headers.get('token'):
			db_deletepaste(getcursor(), pasteid)
			return config.msg_paste_deleted, 200
		else:
			return config.msg_err_401, 401

@app.route('/plain/<pasteid>', methods=['GET', 'DELETE'])
@app.route('/raw/<pasteid>', methods=['GET', 'DELETE'])
def viewraw(pasteid):
	if request.method == 'GET':
		result = db_getpaste(getcursor(cursor_factory=DictCursor), pasteid)
		if not result:
			return config.msg_err_404, 404
		if result['burn'] == 0 or result['expiration'] < datetime.utcnow():
			db_deletepaste(getcursor(), pasteid)
			return config.msg_err_404, 404
		elif result['burn'] > 0:
			db_burn(getcursor(), pasteid)

		pasteview(getcursor()) #count towards total paste views

		return set_cache_control(plain(result['paste']), config.paste_max_age)

	elif request.method == 'DELETE':
		result = db_getpaste(getcursor(cursor_factory=DictCursor), pasteid)
		if not result:
			return config.msg_err_404, 404
		elif 'token' in request.form and result['token'] == request.form['token']:
			db_deletepaste(getcursor(), pasteid)
			return config.msg_paste_deleted, 200
		elif 'token' in request.headers and result['token'] == request.headers.get('token'):
			db_deletepaste(getcursor(), pasteid)
			return config.msg_paste_deleted, 200
		else:
			return config.msg_err_401, 401
	else:
		return "invalid http method\n"

@app.route('/<pasteid>/<token>', methods=['GET'])
def	deletepaste(pasteid, token):
	result = db_getpaste(getcursor(cursor_factory=DictCursor), pasteid)
	if not result:
		abort(404)
	elif result['token'] == token:
		db_deletepaste(getcursor(), pasteid)
		return render_template('deleted.html')
	else:
		abort(401)

@app.route('/about/api')
def aboutapi():
	return set_cache_control(make_response(render_template('api.html')), config.nonpaste_max_age)

@app.route('/about')
def aboutpage():
	return set_cache_control(make_response(render_template('about.html')), config.nonpaste_max_age)

@app.route('/stats')
def statspage():
	stats = getstats(getcursor(cursor_factory=DictCursor))
	return set_cache_control(make_response(render_template('stats.html', stats=stats)), config.nonpaste_max_age)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500




if __name__ == '__main__':
	app.debug = False
	app.run()
