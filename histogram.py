import os
import networkx as nx
import community
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

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
bins = range(1,max(degrees.values())+2)
counts = plt.hist(degrees.values(), bins, color='green',alpha=0.8,rwidth=0.8)
cvals = counts[0].astype(int)
plt.xticks([])
bin_centers = 0.5 * np.diff(bins) + bins[:-1]
for count, x in zip(cvals, bin_centers):
    # Label the x-tics
    plt.annotate(int(x-0.5), xy=(x, 0), xycoords=('data', 'axes fraction'),
        xytext=(0, -3), textcoords='offset points', va='top', ha='center')
    # Label the raw counts
    plt.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
        xytext=(0, -18), textcoords='offset points', va='top', ha='center')
plt.savefig("degreehist.png")
plt.close()

#number of nodes in cluster pic - 218 cluster
ncluster = partition.values()
bins = range(max(ncluster)+1)
plt.hist(ncluster,bins,color='green', alpha=0.8)
plt.savefig("clusthist.png")
plt.close()
