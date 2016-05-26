import os
import networkx as nx
import community
import sqlite3

dbname = "vl_ww.sqlite"
# calculate sum length of alternatives roads
def calck_sum_length (graph, my_path):
	H=graph.subgraph(my_path)
	sum_l=0.0
	for edge in H.edges(data=True):
		if isinstance(edge[2].get('weight'),float):
			sum_l+=edge[2].get('weight')
	return sum_l

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

# find partitions with Louvain's method
partition = community.best_partition(G)

# transform partitions to node and edge lists
count = 0
vul_edges = []
roads = []
len_roads = []

for Ncom in set(partition.values()) :
    list_nodes = [nodes for nodes in partition.keys()
                                if partition[nodes] == Ncom]
    for node in list_nodes:
        G.node[node]['Ncom'] = count
        all_edges_for_node = list(G.edges_iter(node))
        for edge in all_edges_for_node:
            if edge[1] not in list_nodes:
                G.edge[edge[0]][edge[1]]['Vul'] = 1
                vul_edges.append(edge)
            else:
                G.edge[edge[0]][edge[1]]['Vul'] = 0
        all_edges_for_node = []
    count = count + 1
    list_nodes=[]

# find most vulnerable roads
for edge in vul_edges:
    if G.has_edge(edge[0], edge[1]):
        G.remove_edge(edge[0], edge[1])
        if nx.has_path(G, edge[0], edge[1]):
            roads=nx.shortest_path(G, edge[0], edge[1],'weight')
            len_r = calck_sum_length(G, roads)
        else:
            len_r = 99999999.99999999
        G.add_edge(edge[0], edge[1])
        G.edge[edge[0]][edge[1]]['Vul_Val'] = len_r

# export in database
try:
    dbcur.execute("alter table 'Link' add column 'Vul_Val' 'float' default 0.0")
except:
    pass

dbcur.execute("UPDATE Link SET Vul_Val=0.0")
for edge in vul_edges:
    SqlString = 'UPDATE Link SET Vul_Val = ? WHERE (node_a = ?) AND (node_b = ?);'
    dbcur.execute(SqlString, [G.edge[edge[0]][edge[1]]['Vul_Val'], edge[0], edge[1]])

dbcon.close()