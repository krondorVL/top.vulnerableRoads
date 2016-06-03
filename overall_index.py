import sqlite3

dbname = "vl_ww.sqlite"
# database connect
dbcon = sqlite3.connect(dbname)
dbcon.execute('pragma journal_mode = off;')
dbcon.execute('pragma synchronous = 0;')
dbcon.isolation_level = None
dbcur = dbcon.cursor()

# find constants for normalization
SqlString = "Select max(DegreeCentr), max(BtwCentr), max(Vul_Val) from Link;"
dbcur.execute(SqlString)
result = dbcur.fetchall()
maxDegree = float(result[0][0])
maxBtw = float(result[0][1])
maxVul = float(result[0][2])

# update fields
SqlString = "Select link, bearing_a, bearing_b, setback_a from Link;"
dbcur.execute(SqlString)
for row in dbcur.fetchall():
    link = row[0]
    DC = float(row[1])
    BC = float(row[2])
    VV = float(row[3])
    OV = 0.33*DC/maxDegree+0.33*BC/maxBtw+0.33*VV/maxVul
    SqlString = 'UPDATE Link SET setback_b = ? WHERE link = ? ;'
    dbcur.execute(SqlString, [OV, link])






