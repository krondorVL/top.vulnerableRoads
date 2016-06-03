import os
import networkx as nx
import sqlite3

dbname = "vl_ww.sqlite"
# database connect
dbcon = sqlite3.connect(dbname)
dbcon.execute('pragma journal_mode = off;')
dbcon.execute('pragma synchronous = 0;')
dbcon.isolation_level = None
dbcur = dbcon.cursor()

# import data
SqlString = "Select node_a, node_b, length from Link;"
dbcur.execute(SqlString)
if os.path.exists("graph.txt"):
    os.remove("graph.txt")
with open("graph.txt", "w") as out:
    for row in dbcur.fetchall():
        out.write("%d,%d,%f\n" % (row[0], row[1], row[2]))
out.close()

G=nx.read_edgelist('graph.txt',delimiter=',', nodetype=int, data=(('weight',float),))
os.remove("graph.txt")

degrees = G.degree()
btw_centr = nx.edge_betweenness_centrality(G,normalized=False, weight='weight')

# export in database
try:
    dbcur.execute("alter table 'Link' add column 'BtwCentr' 'float'")
except:
    pass
try:
    dbcur.execute("alter table 'Link' add column 'DegreeCentr' 'float'")
except:
    pass

for node in degrees:
    SqlString = 'UPDATE Link SET DegreeCentr = ?, bearing_a = ? WHERE (node_a = ?);'
    dbcur.execute(SqlString, [degrees[node], degrees[node], node])

for node in degrees:
    SqlString = 'UPDATE Link SET DegreeCentr = DegreeCentr + ?, bearing_a = bearing_a + ? WHERE (node_b = ?);'
    dbcur.execute(SqlString, [degrees[node], degrees[node], node])

for edge in btw_centr:
    SqlString = 'UPDATE Link SET BtwCentr = ?, bearing_b = ? WHERE (node_a = ?) AND (node_b = ?);'
    dbcur.execute(SqlString, [btw_centr[edge], btw_centr[edge], edge[0], edge[1]])

dbcon.close()