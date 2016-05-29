#!/usr/bin/env python3

import pygments

from flask import Flask, render_template, url_for, request


app = Flask(__name__)

lexer = 'txt' 
ttl = 60

@app.route('/', methods=['GET', 'POST'])
def index():
	
	if request.method == 'POST':
		if request.form['lexer']:
			lexer = request.form['lexer']
		if request.form['ttl']:
			ttl = int(request.form['ttl'])

	return render_template('index.html')


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')