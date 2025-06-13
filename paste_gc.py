#!/usr/bin/env python3

from datetime import datetime
import psycopg2

from config import dsn

with psycopg2.connect(dsn) as db:
    with db.cursor() as cur:
        r = cur.execute("""DELETE FROM pastes WHERE expiration < %s""", (datetime.utcnow(),))
        print(r)
