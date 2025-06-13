import os

from psycogreen.gevent import patch_psycopg

def post_fork(server, worker):
        patch_psycopg()

try:
    workers = os.process_cpu_count() * 2 + 1 #python 3.13+ only
except AttributeError:
    workers = os.cpu_count() * 2 + 1

bind = "0.0.0.0:8000"
worker_class = "gevent"
