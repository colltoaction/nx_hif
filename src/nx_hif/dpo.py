"""
DPO rewriting for hypergraphs (Bonchi et al):
1. find a matching subgraph
2. identify subgraph nodes with replacement nodes
3. isolate subgraph nodes not in the replacement
4. plug in replacement

https://en.wikipedia.org/wiki/Double_pushout_graph_rewriting
https://arxiv.org/pdf/2012.01847
https://www.researchgate.net/publication/220713176_Algebraic_Approaches_to_Graph_Transformation_-_Part_I_Basic_Concepts_and_Double_Pushout_Approach
"""
import itertools
import networkx as nx


def dpo_production(G, L, R, K, d):
    """
    A graph transformation rule.
    A production in the doublepushout approach is usually de ned as a span ie a pair of graph morphisms with common source In the formal de nition that follows a production is de ned instead as a structure p L l K r R where l and r are the usual two morphisms and the additional component p is the production name.
    a pair L l K r Rof graph homomorphisms from a common interface graph Kand adirect derivation consists of two gluing diagrams of graphs and total graph morphisms"""

def dpo_match(G: nx.MultiDiGraph, L: nx.MultiDiGraph):
    """
    Occurrences of the lefthand side of a production in a graph.
    A match m:LtoG for a production p is a graph homomorphism mapping nodes and edges of L to G in such a way that the graphical structure and the labels are preserved.
    This subgraph matching algorithm is naive and prohibitive in general."""
    G_labels = nx.MultiDiGraph((n for n, d in G.nodes(data=True) if d["bipartite"] == 0))
    L_labels = nx.MultiDiGraph((n for n, d in L.nodes(data=True) if d["bipartite"] == 0))
    itertools.combinations((d["bipartite"], d["node"]) for n, d in L_labels.nodes(data=True))
    # all subgraphs of G matching L_labels
    # then isomorphism but with same number of nodes and label counts

    # in the case of inets we know we have an active/inactive state for wires (nodes)
    # and how to obtain the two adjacent combinators (edges).
    if L_labels.nodes not in G_labels.nodes:
        return

    # TODO self loop would first need to account for the interface
    # because it becomes two wires (nodes) in the subgraph
    matcher = nx.isomorphism.MultiDiGraphMatcher(
        G, L,
        lambda n1, n2:
            n1["bipartite"] == n2["bipartite"] == 0 or
            (n1["bipartite"] == n2["bipartite"] == 1 and n1["tag"] == n2["tag"]),
        lambda _a, _b: True)
    # return match, replacement, boundary



def inet_find_wire(inet: nx.MultiDiGraph, comb, port):
    """
    We use the bipartite attribute, directedness, key and label to build
    a unique node id for a new graph.
    """
    assert inet.nodes[comb]["bipartite"] == 1
    if port == 0:
        for _, w1, _ in inet.out_edges(comb, keys=True):
            return w1
        assert False

    for w1, _, j in inet.in_edges(comb, keys=True):
        if port == j:
            return w1
    assert False


def dpo_morphism(G, H):
    """Graph morphisms are needed to identify the match of a left-hand side of a rule in a (potentially larger) host graph. As we will see below, they are also required for other purposes, such as graph gluing and graph transformation rules."""

def dpo_rule(L, K, R, KtoR):
    """rule applications"""

def dpo_embedding(G, pL, K):
    """rule applications"""

def dpo_context(G, pL, K):
    """rule applications"""

def dpo_derivation(G, pL, pR, m):
    """rule applications, the systems computations"""

def dpo_pushout():
    """a pushout is a sort of generalized union that speci es how to merge together two states having a common substate """

def dpo_model_of_computation():
    """d an adequate notion of equivalence on graphs and derivations that provides representation independence as well as abstraction of the order of independent concurrent derivation step"""

def dpo_grammar(P, G0):
    """ A graph grammar G is a pair G hp L l K r Rp PG0i where the rst component is a family of productions indexed by production names in P and G0 is the start graph c"""

def inet_merge_many_wires(G: nx.MultiDiGraph, ws):
    w = G.number_of_nodes()
    G.add_node(w, bipartite=0)
    for w0 in ws:
        G.add_edges_from(list((y, w, z, d) for y, _, z, d in G.in_edges(w0, data=True, keys=True)))
        G.add_edges_from(list((w, y, z, d) for _, y, z, d in G.out_edges(w0, data=True, keys=True)))
        G.remove_edges_from(list(G.in_edges(w0, keys=True)))
        G.remove_edges_from(list(G.out_edges(w0, keys=True)))
    return w

def inet_rewrite(G: nx.MultiDiGraph, rule):
    """
    A DPO rule consists of three graphs
    specifying what to extract, what to plug in,
    and how to respect some interfaces.
    The ifaces is not HIF.
    """
    match, replacement, ifaces = rule
    G.add_edges_from(list(replacement.in_edges(data=True, keys=True)))
    G.add_edges_from(list(replacement.out_edges(data=True, keys=True)))
    G.add_nodes_from(list(replacement.nodes(data=True)))
    G.remove_edges_from(list(match.in_edges(keys=True, data=True)))
    G.remove_edges_from(list(match.out_edges(keys=True, data=True)))
    ccs = nx.connected_components(nx.to_undirected(ifaces))
    for cc in ccs:
        if len(cc) > 1:
            inet_merge_many_wires(G, cc)
    return G
