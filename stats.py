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

