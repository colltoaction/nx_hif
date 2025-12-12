from .hif import hif_create, hif_new_node, hif_new_edge, hif_add_incidence, hif_nodes, hif_edges
from .readwrite import encode_hif_data, read_hif_data
import json

def test_new_functions_bidirectionality():
    G = hif_create()

    # Create nodes using new function
    n1 = hif_new_node(G, label="node1")
    n2 = hif_new_node(G, label="node2")
    n3 = hif_new_node(G, label="node3")

    assert n1 == 0
    assert n2 == 1
    assert n3 == 2

    # Create edges using new function
    e1 = hif_new_edge(G, label="edge1")
    e2 = hif_new_edge(G, label="edge2")

    assert e1 == 0
    assert e2 == 1

    hif_add_incidence(G, e1, n1, direction="head")
    hif_add_incidence(G, e1, n2, direction="tail")
    hif_add_incidence(G, e2, n2, direction="head")
    hif_add_incidence(G, e2, n3, direction="tail")

    # Verify data integrity
    assert len(hif_nodes(G)) == 3
    assert len(hif_edges(G)) == 2

    # Test encode - read_data bidirectionality
    data = encode_hif_data(G)

    G_read = read_hif_data(data)

    # Verify G_read structure
    assert len(hif_nodes(G_read)) == 3
    assert len(hif_edges(G_read)) == 2

    data_read = encode_hif_data(G_read)

    # Sort lists in data for comparison since order might not be guaranteed
    def sort_data(d):
        d['incidences'].sort(key=lambda x: (x['edge'], x['node']))
        d['nodes'].sort(key=lambda x: x['node'])
        d['edges'].sort(key=lambda x: x['edge'])
        return d

    assert sort_data(data) == sort_data(data_read)

def test_complex_graph_bidirectionality():
    G = hif_create(network_type="complex_test")

    nodes = []
    for i in range(5):
        nodes.append(hif_new_node(G, val=i))

    edges = []
    for i in range(3):
        edges.append(hif_new_edge(G, val=i))

    # Edge 0 connects Node 0 and Node 1
    hif_add_incidence(G, edges[0], nodes[0], direction="head")
    hif_add_incidence(G, edges[0], nodes[1], direction="tail")

    # Edge 1 connects Node 1, Node 2, Node 3 (hyperedge)
    hif_add_incidence(G, edges[1], nodes[1], direction="head")
    hif_add_incidence(G, edges[1], nodes[2], direction="tail")
    hif_add_incidence(G, edges[1], nodes[3], direction="tail")

    # Edge 2 is a loop on Node 4
    hif_add_incidence(G, edges[2], nodes[4], direction="head")
    hif_add_incidence(G, edges[2], nodes[4], direction="tail")

    data = encode_hif_data(G)
    G_read = read_hif_data(data)
    data_read = encode_hif_data(G_read)

    def sort_data(d):
        d['incidences'].sort(key=lambda x: (x['edge'], x['node'], x.get('direction', 'head')))
        d['nodes'].sort(key=lambda x: x['node'])
        d['edges'].sort(key=lambda x: x['edge'])
        return d

    assert sort_data(data) == sort_data(data_read)
