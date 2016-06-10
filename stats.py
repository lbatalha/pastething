from psycopg2.extras import DictCursor
from datetime import datetime

def pastecount(db):
	with db.cursor() as cur:
		cur.execute("UPDATE stats SET counter = counter + 1 WHERE metric='totalpastes';")
	dailystats(db, 'pastecount', datetime.utcnow().date())

def pasteview(db):
	with db.cursor() as cur:
		cur.execute("UPDATE stats SET counter = counter + 1 WHERE metric='totalviews';")
	dailystats(db, 'pasteviews', datetime.utcnow().date())

def dailystats(db, metric, today):
	with db.cursor() as cur:
		cur.execute("""INSERT INTO dailystats (date, {}) \
				VALUES (%s, %s) \
				ON CONFLICT (date) \
				DO UPDATE SET {} = dailystats.{} + 1 \
				WHERE dailystats.date=%s;""".format(metric, metric, metric), \
				(today, 1, today))

def getstats(db):
	stats = {}
	with db.cursor(cursor_factory = DictCursor) as cur:
		cur.execute("SELECT * FROM dailystats WHERE date=%s;", (datetime.utcnow().date(),))
		stats['daily'] = cur.fetchone()
		cur.execute("SELECT * FROM stats;")
		totalstats = {}
		for i in cur.fetchall():
			totalstats[i[0]] = i[1]
		stats['total'] = totalstats
		print()
		return stats

def growthgraph(db):
	#TODO: fancy histogram with site usage
	return True

def expirationgraph(db):
	csv = []
	#TODO: fancy histogram with calculated paste expiration
	return True
