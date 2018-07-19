[![Build Status](https://travis-ci.org/lbatalha/pastething.svg?branch=master)](https://travis-ci.org/lbatalha/pastething)
# A python3-flask pastebin

Example: https://cpy.pt/

## Dependencies

* postgresql-9.5 <
* python3 (3.3+)
* python3-flask
* python3-pygments
* python3-psycopg2

## Installation

* install dependencies
	* ```
		pip install -r requirements.txt
		```
* setup db with schema.sql
	* ```
		sudo -u postgres psql -f schema.db
		```
* copy config.py.example as config.py
	* ```
		cp config.py.example config.py
		```
* configure config.py - **make sure secret_key and domain are changed!**
* use whatever wsgi server you want - (gunicorn!)


## nginx config used for cpy.pt

```
server {
        listen 443 http2;
        listen [::]:443 http2;
        server_name cpy.pt;

        keepalive_timeout 5;

        client_max_body_size 2M;

        ssl_certificate /etc/letsencrypt/live/cpy.pt/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/cpy.pt/privkey.pem;

        ssl on;
        ssl_session_cache  builtin:1000  shared:SSL:20m;
        ssl_session_timeout 5m;
        ssl_protocols  TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';
        ssl_prefer_server_ciphers on;
        ssl_dhparam /etc/ssl/certs/dhparam.pem;
        ssl_stapling on;
        ssl_stapling_verify on;
        resolver 8.8.8.8 8.8.4.4 valid=300s;
        resolver_timeout 5s;

        add_header X-Frame-Options "DENY";
        add_header Strict-Transport-Security "max-age=31536000; includeSubdomains; preload";
        add_header X-Content-Type-Options nosniff;
        add_header X-Xss-Protection "1; mode=block";
        add_header Content-Security-Policy "default-src none; style-src 'self'; script-src 'self'";

        location / {
                proxy_http_version 1.1;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_set_header Host $http_host;
                proxy_redirect off;
                proxy_read_timeout 30;
                proxy_pass http://unix:/var/run/pastebin/cpy.pt.sock:;
        }

        location /static {
                root /home/pastebin/pastething/;
                add_header Cache-Control "public, max-age=864000";

        }
        location =/robots.txt {
                root /home/pastebin/pastething/;
        }

}
```

## Service configuration used in cpy.pt

In production, cpy.pt uses gunicorn with gevent workers, to use gevent with psycopg2 without blocking issues you must monkeypatch the app (see below)

### Example systemd service file template:
```
[Unit]
Description=cpy.pt gunicorn daemon
After=network.target

[Service]
User=pastebin
Group=pastebin
WorkingDirectory=/home/pastebin/pastething
PIDFile=/var/run/pastebin/cpy.pt.pid
ExecStart=/usr/local/bin/gunicorn --config /home/pastebin/pastething/gunicorn.conf.py --pid /var/run/pastebin/cpy.pt.pid -w {{2 * ansible_processor_count + 1}} -k gevent -b unix:/var/run/pastebin/cpy.pt.sock main:app
ExecReload=/bin/kill -1 $MAINPID
ExecStop=/bin/kill -15 $MAINPID
PrivateTmp=false

[Install]
WantedBy=multi-user.target
```

### Example gunicorn config file

Only the post-fork hook is defined in the cpy.pt config file, the service specific configs are defined in the systemd service file above.
This will monkeypatch psycopg every time a new worker is forked.
```
from psycogreen.gevent import patch_psycopg

def post_fork(server, worker):
	patch_psycopg()
```

To validate that you dont have blocking issues simply add a long timer to a db endpoint and simultaneously query that endpoint and one that does not have any blocking calls.
The easiest way is to add `cur.execute("SELECT pg_sleep(1);")` just before the return statement of the `getstats` function, then simply setup some load testing application to hit the `/about` and `/stats` endpoint.
The desired behaviour is the `/about` endpoint having normal response times (few mileseconds) and the `/stats` endpoint having >1s response times.
If the `/about` endpoint does not have consistent response times then you are blocking.

You can also use the `eventlet` worker type with gunicorn as this should automatically patch psycopg2 and the difference will be obvious.


### gc.py

This file is just a simple script used to delete all expire pastes.
Although all expired pastes are deleted when they are requested, that still leaves the possibility of stale pastes. This makes sure we dont leave garbage behind.
This is preferable to running the garbage collection query on every request to reduce overhead.

The easiest way to set this up is using cron.
cpy.pt uses a 5 minute timer.
