import networkx as nx
import community
import sqlite3

# import data, find partitions
G=nx.read_edgelist('table.csv',delimiter=',', nodetype=int, data=(('weight',float),('link',int),('osmid',int),))

Vul_G = nx.Graph()

partition = community.best_partition(G)
count = 0
vul_edges = []
roads = []
len_roads = []

def calck_sum_length (graph, my_path):
	H=graph.subgraph(my_path)
	sum_l=0.0
	for edge in H.edges(data=True):
		if isinstance(edge[2].get('weight'),float):
			sum_l+=edge[2].get('weight')
	return sum_l

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

# intersections
for edge in vul_edges:
    if G.has_edge(edge[0], edge[1]):
        G.remove_edge(edge[0], edge[1])
        if nx.has_path(G, edge[0], edge[1]):
            roads=nx.shortest_path(G, edge[0], edge[1],'weight')
            len_r = calck_sum_length(G, roads)
        else:
            len_r = 99999999.0
        Vul_G.add_edge(edge[0],edge[1], Vul_Val=len_r)
        G.add_edge(edge[0], edge[1])
        G.edge[edge[0]][edge[1]]['Vul_Val'] = len_r