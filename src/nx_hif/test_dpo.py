import networkx as nx
from .dpo import *


def inet_franchu():
    inet = nx.MultiDiGraph()
    inet.add_node(0, bipartite=1, tag="construct")
    inet.add_node(1, bipartite=1, tag="duplicate")
    inet.add_node(2, bipartite=1, tag="construct")
    inet.add_node(3, bipartite=1, tag="erase")
    inet.add_node(4, bipartite=0)
    inet.add_node(5, bipartite=0)
    inet.add_node(6, bipartite=0)
    inet.add_node(7, bipartite=0)
    inet.add_node(8, bipartite=0)
    inet.add_edge(0, 5, key=0, tag=0)
    inet.add_edge(4, 0, key=1)
    inet.add_edge(4, 0, key=2)
    inet.add_edge(1, 5, key=0, tag=1)
    inet.add_edge(6, 1, key=1)
    inet.add_edge(6, 2, key=1)
    inet.add_edge(2, 7, key=0, tag=2)
    inet.add_edge(7, 1, key=2)
    inet.add_edge(8, 2, key=2)
    inet.add_edge(3, 8, key=0, tag=3)
    return inet

def inet_condup_rule_L():
    L = nx.MultiDiGraph()
    L.add_node(0, bipartite=1, tag="construct")
    L.add_node(1, bipartite=1, tag="duplicate")
    L.add_node(2, bipartite=0)
    L.add_node(3, bipartite=0, tag=0)
    L.add_node(4, bipartite=0, tag=1)
    L.add_node(5, bipartite=0, tag=2)
    L.add_node(6, bipartite=0, tag=3)
    L.add_edge(0, 2, key=0)
    L.add_edge(3, 0, key=1)
    L.add_edge(4, 0, key=2)
    L.add_edge(1, 2, key=0)
    L.add_edge(5, 1, key=0)
    L.add_edge(6, 1, key=0)
    return L

def inet_condup_rule_R():
    R = nx.MultiDiGraph()
    R.add_node(0, bipartite=1, tag="construct")
    R.add_node(1, bipartite=1, tag="construct")
    R.add_node(2, bipartite=1, tag="duplicate")
    R.add_node(3, bipartite=1, tag="duplicate")
    R.add_node(4, bipartite=0, tag=0)
    R.add_node(5, bipartite=0)
    R.add_node(6, bipartite=0)
    R.add_node(7, bipartite=0, tag=1)
    R.add_node(8, bipartite=0)
    R.add_node(9, bipartite=0)
    R.add_node(10, bipartite=0, tag=2)
    R.add_node(11, bipartite=0, tag=3)
    R.add_edge(0, 4, key=0)
    R.add_edge(5, 0, key=1)
    R.add_edge(6, 0, key=2)
    R.add_edge(1, 7, key=0)
    R.add_edge(8, 1, key=1)
    R.add_edge(9, 1, key=2)
    R.add_edge(2, 10, key=0)
    R.add_edge(5, 2, key=1)
    R.add_edge(9, 2, key=2)
    R.add_edge(3, 11, key=0)
    R.add_edge(6, 3, key=1)
    R.add_edge(8, 3, key=2)
    return R

def test_condup():
    L = inet_condup_rule_L()
    R = inet_condup_rule_R()
    inet = inet_franchu()
    inet = dpo_rewrite(inet, L, R)
    assert len(inet.edges) == 16
