import networkx as nx
import json

def write_hif(G, path):
    pass

def add_incidence(G: nx.Graph, incidence):
    edge_id = incidence["edge"]
    node_id = incidence["node"]
    G.add_node(edge_id, bipartite=1)
    G.add_node(node_id, bipartite=0)
    G.add_edge(edge_id, node_id)

def add_edge(G: nx.Graph, edge):
    attrs = edge.get("attr", {})
    edge_id = edge["edge"]
    if "weigth" in edge:
        attrs["weigth"] = edge["weigth"]
    for attr_key, attr_value in attrs.items():
        if not G.has_node(edge_id):
            G.add_node(edge_id, bipartite=1)
        G.nodes[edge_id][attr_key] = attr_value

def add_node(G: nx.Graph, node):
    attrs = node.get("attr", {})
    node_id = node["node"]
    if "weigth" in node:
        attrs["weigth"] = node["weigth"]
    for attr_key, attr_value in attrs.items():
        if not G.has_node(node_id):
            G.add_node(node_id, bipartite=0)
        G.nodes[node_id][attr_key] = attr_value

def read_hif(path):
    with open(path) as file:
        data = json.loads(file.read())
    return read_hif_data(data)

def read_hif_data(data):
    G_attrs = data.get("metadata", {})
    if "network-type" in data:
        G_attrs["network-type"] = data["network-type"]
    G = nx.Graph(**G_attrs)
    for i in data["incidences"]:
        add_incidence(G, i)
    for e in data["edges"]:
        add_edge(G, e)
    for n in data["nodes"]:
        add_node(G, n)
    return G
