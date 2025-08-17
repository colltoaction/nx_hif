import networkx as nx


def hif_nodes(G: nx.MultiDiGraph, data=False):
    for n, d in G.nodes(data=True):
        if d["bipartite"] == 0:
            yield (n, d["node"], d) if data else (n, d["node"])

def hif_edges(G: nx.MultiDiGraph, data=False):
    for e, d in G.nodes(data=True):
        if d["bipartite"] == 1:
            yield (e, d["edge"], d) if data else (e, d["edge"])

def hif_edge_nodes(G: nx.MultiDiGraph, edge=None, data=False):
    for e0, e1 in hif_edges(G):
        if edge is None or edge == e1:
            for e in G.in_edges(e0, keys=True, data=data):
                ed = G.nodes[e[1]]["edge"]
                no = G.nodes[e[0]]["node"]
                yield (ed, no, "tail",) + e[2:]
            for e in G.out_edges(e0, keys=True, data=data):
                ed = G.nodes[e[0]]["edge"]
                no = G.nodes[e[1]]["node"]
                yield (ed, no, "head",) + e[2:]

def hif_incidences(G: nx.MultiDiGraph, edge=None, node=None, direction=None, key=None, data=False):
    for e in hif_edge_nodes(G, edge, data=data):
        if node is None or node == e[1]:
            if direction is None or direction == e[2]:
                if key is None or key == e[3]:
                    yield e

def hif_add_edge(G, edge, **attr):
    if not G.has_node(edge):
        G.add_node(("edge", edge), bipartite=1)
    attr["edge"] = edge
    for attr_key, attr_value in attr.items():
        G.nodes[("edge", edge)][attr_key] = attr_value

def hif_add_node(G, node, **attr):
    if not G.has_node(node):
        G.add_node(("node", node), bipartite=0)
    attr["node"] = node
    for attr_key, attr_value in attr.items():
        G.nodes[("node", node)][attr_key] = attr_value

def hif_add_incidence(G: nx.MultiDiGraph, edge, node, direction, key, **attr):
    x = None
    y = None
    for e0, e1 in hif_edges(G):
        if edge == e1:
            x = e0
    for n0, n1 in hif_nodes(G):
        if node == n1:
            y = n0
    if x is None:
        x = ("edge", edge)
        G.add_node(x, bipartite=1, edge=edge)
    if y is None:
        y = ("node", node)
        G.add_node(y, bipartite=0, node=node)
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
