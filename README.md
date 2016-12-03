#A python3-flask pastebin

Example: https://cpy.pt/

##Dependencies

* postgresql-9.5 <
* python3 (3.3+)
* python3-flask
* python3-pygments
* python3-psycopg2

##Installation

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


## Example nginx config used for cpy.pt

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
				add_header Strict-Transport-Security "max-age=31104000; includeSubdomains; preload";
				add_header X-Content-Type-Options nosniff;
				add_header X-Xss-Protection "1; mode=block";
				add_header Content-Security-Policy "default-src none; style-src 'self'; script-src 'self'";

				location / {
								proxy_http_version 1.1;
								proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
								proxy_set_header Host $http_host;
								proxy_redirect off;
								proxy_read_timeout 30;
								proxy_pass http://unix:/tmp/cpy.pt.sock:;
				}

				location /static {
								root /home/pastebin/pastething/;
								add_header Cache-Control "public, max-age=864000";
				}
}

```
