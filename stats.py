from datetime import datetime

def pastecount(cursor):
    with cursor as cur:
        cur.execute("UPDATE stats SET counter = counter + 1 WHERE metric = 'totalpastes';")
        dailystats(cur, 'pastecount', datetime.utcnow().date())

def pasteview(cursor):
    with cursor as cur:
        cur.execute("UPDATE stats SET counter = counter + 1 WHERE metric = 'totalviews';")
        dailystats(cur, 'pasteviews', datetime.utcnow().date())

def dailystats(cursor, metric, today):
    '''this is only ever called by other stats functions'''
    cursor.execute("""INSERT INTO dailystats (date, {}) \
                VALUES (%s, %s) \
                ON CONFLICT (date) \
                DO UPDATE SET {} = dailystats.{} + 1 \
                WHERE dailystats.date = %s;""".format(metric, metric, metric), \
                (today, 1, today))

def getstats(cursor):
    stats = {}
    with cursor as cur:
        cur.execute("SELECT * FROM dailystats WHERE date = %s;", (datetime.utcnow().date(),))
        stats['daily'] = cur.fetchone()
        cur.execute("SELECT * FROM stats;")
        totalstats = {}
        for i in cur.fetchall():
            totalstats[i[0]] = i[1]
        stats['total'] = totalstats
        return stats
