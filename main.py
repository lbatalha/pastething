#!/usr/bin/env python3

import pygments
from flask import Flask, render_template, url_for, request

app = Flask(__name__)

lexer = 'txt' 
ttl = 60

@app.route('/', methods=['GET', 'POST'])
def newpaste():
	paste = None
	if request.method == 'POST':
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
	return render_template('newpaste.html')


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')