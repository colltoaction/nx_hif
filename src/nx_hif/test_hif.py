import pytest
from .hif import hif_create, hif_add_node, hif_add_edge, hif_new_node, hif_new_edge, hif_nodes, hif_edges, hif_add_incidence

def test_hif_new_node():
    G = hif_create()
    n1 = hif_new_node(G, color="red")
    n2 = hif_new_node(G, color="blue")

    assert n1 == 0
    assert n2 == 1

    nodes = list(hif_nodes(G, data=True))
    nodes.sort(key=lambda x: x[0])
    assert nodes[0] == (0, {"color": "red"})
    assert nodes[1] == (1, {"color": "blue"})

def test_hif_new_edge():
    G = hif_create()
    e1 = hif_new_edge(G, weight=10)
    e2 = hif_new_edge(G, weight=20)

    assert e1 == 0
    assert e2 == 1

    edges = list(hif_edges(G, data=True))
    edges.sort(key=lambda x: x[0])
    assert edges[0] == (0, {"weight": 10})
    assert edges[1] == (1, {"weight": 20})

def test_mixed_add_and_new():
    G = hif_create()
    hif_add_node(G, 0, label="zero")
    # V.number_of_nodes() is 1 now.
    n = hif_new_node(G, label="one")
    assert n == 1

    hif_add_edge(G, 0, label="e_zero")
    e = hif_new_edge(G, label="e_one")
    assert e == 1

def test_user_scenario():
    hif_g = hif_create()
    stream_id = hif_new_node(hif_g, kind="stream")
    e_stream = hif_new_edge(hif_g, kind="event")
    doc_id = hif_new_node(hif_g, kind="document")
    e_doc= hif_new_edge(hif_g, kind="event")

    assert stream_id == 0
    assert e_stream == 0
    assert doc_id == 1
    assert e_doc == 1

    hif_add_incidence(hif_g, e_doc, doc_id, key="start")
    hif_add_incidence(hif_g, e_doc, stream_id, key="next")
    hif_add_incidence(hif_g, e_doc, stream_id, key="end")
