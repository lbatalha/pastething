from time import sleep

import requests
import subprocess

import config

url = "http://localhost:5000/"

def test_plainresponse():
    params = {'paste': 'test', 'raw': 'true'}
    r = requests.post(url, data=params)
    response = r.text.split(" | ")
    r = requests.get(response[0])
    assert r.headers['content-type'] == 'text/plain; charset=utf-8'
    params['raw'] = ''
    r = requests.post(url, data=params)
    response = r.text.split(" | ")
    r = requests.get(response[0])
    assert r.headers['content-type'] == 'text/html; charset=utf-8'

def test_pastedelete():
    params = {'paste': 'test', 'burn': 1, 'ttl': 1.0}
    r = requests.post(url, data=params)
    assert r.status_code == 200
    response = r.text.split(" | ")
    r = requests.delete(response[0], data={'token': response[1][:-1]})
    assert r.status_code == 200

def test_postlimits():
    #Missing paste body test
    params = {'paste': '', 'burn': 1, 'ttl': 1.0}
    r = requests.post(url, data=params)
    assert r.status_code != 200
    params['paste'] = 'test'

    #burn count too high test
    params['burn'] = config.paste_limits['burn_max'] + 1
    r = requests.post(url, data=params)
    assert r.status_code != 200
    params['burn'] = config.paste_limits['burn_max'] - 1

    #ttl too high test
    params['ttl'] = config.paste_limits['ttl_max'] + 0.1
    r = requests.post(url, data=params)
    assert r.status_code != 200
    params['ttl'] = config.paste_limits['ttl_max'] - 0.1

    #burn too low test
    params['burn'] = config.paste_limits['burn_min'] - 1
    r = requests.post(url, data=params)
    assert r.status_code != 200
    params['burn'] = config.paste_limits['burn_min']

    #ttl too low test
    params['ttl'] = config.paste_limits['ttl_min']
    r = requests.post(url, data=params)
    assert r.status_code != 200


def test_pasteburn():
    """test for paste burn auto-deletion"""
    params = {'paste': 'test', 'burn': 2, 'ttl': 1.0}
    r = requests.post(url, data=params)
    assert r.status_code == 200
    response = r.text.split(" | ")
    r = requests.get(response[0])
    assert r.status_code == 200
    r = requests.get(response[0])
    r = requests.get(response[0])
    assert r.status_code == 404

def test_pastettl():
    """test for paste auto-delete on expiration"""
    ttl = 0.001
    seconds = 60*60*0.001
    params = {'paste': 'test', 'ttl': ttl}
    r = requests.post(url, data=params)
    assert r.status_code == 200
    response = r.text.split(" | ")
    r = requests.get(response[0])
    assert r.status_code == 200
    sleep(seconds)
    r = requests.get(response[0])
    assert r.status_code == 404

def test_lexer():
    # basic tests to ensure no errors when defining explicit lexers
    # TODO?: add tests to check requested lexer is used when retrieving paste
    params = {'paste': 'test', 'raw': 'true', 'lexer': 'text'}
    r = requests.post(url, data=params)
    assert r.status_code == 200
    params = {'paste': 'test', 'raw': 'true', 'lexer': 'bash'}
    r = requests.post(url, data=params)
    assert r.status_code == 200
    params = {'paste': 'test', 'raw': 'true', 'lexer': '∞'}
    r = requests.post(url, data=params)
    assert r.status_code == 200


def test_garbagecollect():
    assert subprocess.run(['python3', 'paste_gc.py']).returncode == 0
