#!/usr/bin/env python3

import random

#----

import pygments
from flask import Flask, render_template, url_for, request, abort, redirect

app = Flask(__name__)

lexer = 'txt'
ttl = 60

rng = random.SystemRandom()

url_len = 4
alphabet = tuple("23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz")
base = len(alphabet)

def base_encode(num):
	if not num:
		return alphabet[0]
	result = ''
	while num:
		num, rem = divmod(num, base)
		result = result.join(alphabet[rem])
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
		url = ''
		for i in range(url_len):
			url += base_encode(rng.getrandbits(6))
		print(url)
	
	return render_template('newpaste.html')

@app.route('/<uri>', methods=['GET'])
def viewpaste():
	if request.method == 'GET':
		return render_template('viewpaste.html', paste = paste)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')