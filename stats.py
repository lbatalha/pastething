def pastecount(db):
	with db.cursor() as cur:
		cur.execute("UPDATE stats SET counter = counter + 1 WHERE metric='totalpastes';")

def pasteview(db):
	with db.cursor() as cur:
		cur.execute("UPDATE stats SET counter = counter + 1 WHERE metric='totalviews';")

		        

