import networkx as nx
from .dpo import *
from . import read_hif


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
    L = read_hif("data/inet/condup_rule_L.json")
    B = read_hif("data/inet/condup_rule_L_boundary.json")
    return L, B

def inet_condup_rule_R():
    R = read_hif("data/inet/condup_rule_R.json")
    B = read_hif("data/inet/condup_rule_R_boundary.json")
    return R, B

def inet_dupdup_rule_L():
    L = read_hif("data/inet/dupdup_rule_L.json")
    B = read_hif("data/inet/dupdup_rule_L_boundary.json")
    return L, B

def inet_dupdup_rule_R():
    R = read_hif("data/inet/dupdup_rule_R.json")
    B = read_hif("data/inet/dupdup_rule_R_boundary.json")
    return R, B

def inet_concon_rule_L():
    L = read_hif("data/inet/concon_rule_L.json")
    B = read_hif("data/inet/concon_rule_L_boundary.json")
    return L, B

def inet_concon_rule_R():
    R = read_hif("data/inet/concon_rule_R.json")
    B = read_hif("data/inet/concon_rule_R_boundary.json")
    return R, B

def inet_eracon_rule_L():
    L = read_hif("data/inet/eracon_rule_L.json")
    B = read_hif("data/inet/eracon_rule_L_boundary.json")
    return L, B

def inet_eracon_rule_R():
    R = read_hif("data/inet/eracon_rule_R.json")
    B = read_hif("data/inet/eracon_rule_R_boundary.json")
    return R, B

def inet_eradup_rule_L():
    L = read_hif("data/inet/eradup_rule_L.json")
    B = read_hif("data/inet/eradup_rule_L_boundary.json")
    return L, B

def inet_eradup_rule_R():
    R = read_hif("data/inet/eradup_rule_R.json")
    B = read_hif("data/inet/eradup_rule_R_boundary.json")
    return R, B

def inet_eraera_rule_L():
    L = read_hif("data/inet/eraera_rule_L.json")
    B = read_hif("data/inet/eraera_rule_L_boundary.json")
    return L, B

def inet_eraera_rule_R():
    R = read_hif("data/inet/eraera_rule_R.json")
    B = read_hif("data/inet/eraera_rule_R_boundary.json")
    return R, B


def test_inet_franchu():
    L = inet_condup_rule_L()
    R = inet_condup_rule_R()
    G = inet_franchu()
    K = dpo_invariant(G, L, R)
    G = dpo_rewrite(G, L, R, K)
    assert len(G.edges) == 16

    L = inet_concon_rule_L()
    R = inet_concon_rule_R()
    K = dpo_invariant(G, L, R)
    G = dpo_rewrite(G, L, R, K)
    assert len(G.edges) == 10

    L = inet_dupdup_rule_L()
    R = inet_dupdup_rule_R()
    K = dpo_invariant(G, L, R)
    G = dpo_rewrite(G, L, R, K)
    assert len(G.edges) == 4

    L = inet_eracon_rule_L()
    R = inet_eracon_rule_R()
    K = dpo_invariant(G, L, R)
    G = dpo_rewrite(G, L, R, K)
    assert len(G.edges) == 2

    L = inet_eraera_rule_L()
    R = inet_eraera_rule_R()
    K = dpo_invariant(G, L, R)
    G = dpo_rewrite(G, L, R, K)
    assert len(G.edges) == 0
