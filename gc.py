#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
from datetime import datetime
from config import dsn

with psycopg2.connect(dsn) as db:
	with db.cursor() as cur:
		r= cur.execute("""DELETE FROM pastes WHERE expiration < %s""", (datetime.utcnow(),))
		print(r)
