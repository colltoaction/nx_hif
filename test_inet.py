import networkx as nx
from inet import *


def test_annihilate_erase_erase():
    inet = nx.Graph()
    u = inet_add_erase(inet)
    v = inet_add_erase(inet)
    inet_connect_ports(inet, (u, 0), (v, 0))
    annihilate_erase_erase(inet)
    assert len(inet) == 0


def test_annihilate_construct_duplicate():
    inet = nx.Graph()
    u = inet_add_construct(inet)
    v = inet_add_duplicate(inet)
    inet_connect_ports(inet, (u, 0), (v, 0))
    inet.add_node(1, bipartite=0)
    inet.add_node(2, bipartite=1, tag="construct")
    inet.add_node(3, bipartite=1, tag="duplicate")
    inet.add_edge(1, 2, index=0)
    inet.add_edge(1, 3, index=0)

    annihilate_construct_duplicate(inet)
    assert len(inet.nodes) == 2
    assert len(inet.edges) == 0
