import networkx as nx


def hif_nodes(G: nx.MultiDiGraph, data=False):
    for n, d in G.nodes(data=True):
        if d["bipartite"] == 0:
            yield (n, d["node"], d) if data else (n, d["node"])

def hif_edges(G: nx.MultiDiGraph, data=False):
    for e, d in G.nodes(data=True):
        if d["bipartite"] == 1:
            yield (e, d["edge"], d) if data else (e, d["edge"])

def hif_incidences(G: nx.MultiDiGraph, data=False):
    for nx_id_edge, edge in hif_edges(G):
        for e in G.in_edges(nx_id_edge, keys=True, data=data):
            nx_id_node = e[0]
            node = G.nodes[nx_id_node]["node"]
            yield (nx_id_edge, nx_id_node, edge, node, "tail",) + e[2:]
        for e in G.out_edges(nx_id_edge, keys=True, data=data):
            nx_id_node = e[1]
            node = G.nodes[nx_id_node]["node"]
            yield (nx_id_edge, nx_id_node, edge, node, "head",) + e[2:]

def hif_add_edge(G, edge, **attr):
    x = None
    for e0, e1 in hif_edges(G):
        if edge == e1:
            x = e0
    if x is None:
        x = ("edge", edge)
        G.add_node(x, bipartite=1, edge=edge)
    for attr_key, attr_value in attr.items():
        G.nodes[x][attr_key] = attr_value
    return x

def hif_add_node(G, node, **attr):
    y = None
    for n0, n1 in hif_nodes(G):
        if node == n1:
            y = n0
    if y is None:
        y = ("node", node)
        G.add_node(y, bipartite=0, node=node)
    for attr_key, attr_value in attr.items():
        G.nodes[y][attr_key] = attr_value
    return y

def hif_add_incidence(G: nx.MultiDiGraph, edge, node, direction, key, **attr):
    x = hif_add_edge(G, edge)
    y = hif_add_node(G, node)
    if direction == "tail":
        G.add_edge(y, x, key, **attr)
    else:
        G.add_edge(x, y, key, **attr)

def hif_remove_node(G: nx.MultiDiGraph, node):
    for n0, n in hif_nodes(G):
        if n == node:
            e0 = list(G.in_edges(n0))
            e1 = list(G.out_edges(n0))
            G.remove_edges_from(e0)
            G.remove_edges_from(e1)

def hif_remove_incidence(G: nx.MultiDiGraph, node, key):
    incs = [e
            for n0, n1 in hif_nodes(G)
            if node == n1
            for e in G.out_edges(n0, keys=True)
            if e[2] == key]
    print("incs, node, key:", incs, node, key)
    G.remove_edges_from(incs)
