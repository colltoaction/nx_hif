import gzip
import networkx as nx
import json
from .hif import *


def write_hif(G: HyperGraph, path):
    data = encode_hif_data(G)
    with open(path, "w") as file:
        json.dump(data, file, indent=2)

def encode_hif_data(G: HyperGraph):
    V, E, I = G
    incidences = []
    edges = []
    nodes = []

    # Sort incidences for deterministic output, though not strictly required by JSON
    # We can't easily sort without converting to list first

    for u, v, k, a in hif_incidences(G, data=True):
        a = a.copy()
        if u[1] == V.graph["incidence_pair_index"]:
            u, v = v[0], u[0]
        else:
            u, v = u[0], v[0]

        direction = a.pop("direction", "head")

        incidence = {"edge": u, "node": v}

        # Handle weight
        if "weight" in a:
            incidence["weight"] = a.pop("weight")

        if direction != "head":
            incidence["direction"] = direction

        # Filter out internal key if it exists in attrs (it shouldn't be in 'a' usually as it's passed as k, but check)
        a.pop("key", None)

        # Only add attrs if not empty
        if a:
            incidence["attrs"] = a

        incidences.append(incidence)

    for u, d in hif_nodes(G, data=True):
        a = d.copy()
        node = {"node": u}
        if "weight" in a:
            node["weight"] = a.pop("weight")
        if a:
            node["attrs"] = a
        nodes.append(node)

    for u, d in hif_edges(G, data=True):
        a = d.copy()
        edge = {"edge": u}
        if "weight" in a:
            edge["weight"] = a.pop("weight")
        if a:
            edge["attrs"] = a
        edges.append(edge)

    # Metadata and network-type should be retrieved from I (where hif_create puts them)
    metadata = {k: v for k, v in I.graph.items() if k != "incidence_pair_index"}
    # Pop 'network-type' if present in metadata, to set it top-level
    network_type = metadata.pop("network-type", None)

    result = {
        "metadata": metadata,
        "incidences": incidences,
        "nodes": nodes,
        "edges": edges
    }

    if network_type:
        result["network-type"] = network_type

    return result

def add_incidence(G: HyperGraph, incidence):
    attrs = incidence.get("attrs", {}).copy() # Make sure we don't modify the input dict if reused
    edge_id = incidence["edge"]
    node_id = incidence["node"]
    direction = incidence.get("direction", "head")
    # Use None for key to allow duplicates (multigraph behavior) unless key is specified
    key = attrs.pop("key", None)
    if "weight" in incidence:
        attrs["weight"] = incidence["weight"]
    hif_add_incidence(G, edge_id, node_id, direction, key, **attrs)

def add_edge(G: HyperGraph, edge):
    attrs = edge.get("attrs", {}).copy()
    edge_id = edge["edge"]
    if "weight" in edge:
        attrs["weight"] = edge["weight"]
    hif_add_edge(G, edge_id, **attrs)

def add_node(G: HyperGraph, node):
    attrs = node.get("attrs", {}).copy()
    node_id = node["node"]
    if "weight" in node:
        attrs["weight"] = node["weight"]
    hif_add_node(G, node_id, **attrs)

def read_hif(path):
    with open(path) as file:
        data = json.load(file)
    return read_hif_data(data)

def read_hif_gzip(path):
    with gzip.open(path, "r") as fin:
        data = json.load(fin)
    return read_hif_data(data)

def read_hif_data(data):
    G_attrs = data.get("metadata", {})
    if "network-type" in data:
        G_attrs["network-type"] = data["network-type"]
    G = hif_create(**G_attrs)
    for i in data["incidences"]:
        add_incidence(G, i)
    for e in data.get("edges", []):
        add_edge(G, e)
    for n in data.get("nodes", []):
        add_node(G, n)
    # note that this is the standard technique for disjoint unions.
    # it means ids are not preserved and we need to save edge and node ids in attributes.
    # G = nx.convert_node_labels_to_integers(G)
    return G
