import os
import networkx as nx
import community
import sqlite3
import matplotlib.pyplot as plt

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

#G=nx.read_edgelist('graph.txt',delimiter=',', nodetype=int, create_using=nx.DiGraph(), data=(('weight',float),)) - TypeError: Bad graph type, use only non directed graph
G=nx.read_edgelist('graph.txt',delimiter=',', nodetype=int, data=(('weight',float),))
os.remove("graph.txt")

# find partitions with Louvain's method, degrees with networkxX
partition = community.best_partition(G)
degrees = G.degree()

#degree hist pic
bins = range(1,max(degrees.values())+1)
plt.hist(degrees.values(), bins, color='green',alpha=0.8,rwidth=0.8)
plt.xticks(bins)
plt.savefig("degreehist.png")
plt.close()

#number of nodes in cluster pic - 218 cluster
ncluster = partition.values()
bins = range(max(ncluster)+1)
plt.hist(ncluster,bins,color='green', alpha=0.8)
plt.savefig("clusthist.png")
plt.close()
