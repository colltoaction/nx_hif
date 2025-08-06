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


def dpo_rewrite(G: nx.MultiDiGraph, L: nx.MultiDiGraph, R: nx.MultiDiGraph):
    """
    To rewrite 𝐺 into 𝐻 we compute the object 𝐶 for the
    pushout complement 𝐾 −→ 𝐶 −→ 𝐺 of 𝐾 −→ 𝐿 −𝑚→ 𝐺.
    𝐶 holds the part of 𝐺 that isn't matched by 𝑚,
    so we form the the span 𝐶 ←− 𝐾 −→ 𝑅,
    and obtain 𝐻 as the pushout.
    """
    # Rule authors will tag their L and R boundary wires.
    K = dpo_invariant(L, R)

    # To find a match we first have to remove the boundary nodes from L.
    # This is necessary to use isomorphism in cases such as self-loops.
    L.remove_nodes_from(l for l, d in K.nodes if d["bipartite"] == 0)
    matcher = nx.isomorphism.MultiDiGraphMatcher(
        G, L,
        lambda n1, n2:
            n1["bipartite"] == n2["bipartite"] == 0 or
            (n1["bipartite"] == n2["bipartite"] == 1 and n1["tag"] == n2["tag"]),
        lambda _a, _b: True)

    for iso in matcher.subgraph_isomorphisms_iter():
        # each boundary wire has exactly one edge.
        # the other end is a hyperedge with port that is part of the isomorphic subgraph,
        # with translation G-->L.
        # from L
        for port in K.in_edges:
            iso[L[port]]
        # to R
        for port in K.out_edges:
            R[iso[port]]
 
        # TODO We reattach R removing its boundary,
        # and replacing each old edge from the boundary wire to a port
        # with a similar edge from the inner boundary to the port.
        # when tagging the inner boundary we might have multiple tags for one wire, self loop
        C = nx.MultiDiGraph(G)
        C.remove_nodes_from(iso)
        # We obtain 𝐻 from the pushout of 𝐶 ←− 𝐾 −→ 𝑅.
        C.add_edges_from(list(R.in_edges(data=True, keys=True)))
        C.add_edges_from(list(R.out_edges(data=True, keys=True)))
        C.add_nodes_from(list(R.nodes(data=True)))
        C.remove_edges_from(list(C.in_edges(keys=True, data=True)))
        C.remove_edges_from(list(C.out_edges(keys=True, data=True)))
        return C
    return G

def dpo_invariant(L, R):
    """
    The invariant subgraph 𝐾 is upgraded from a discrete hypergraph
    consisting of the inputs and the outputs of the two sides of the rule,
    to a mapping between L and R boundary nodes.
    """
    K = nx.MultiDiGraph()
    L_boundary = sorted(
        ((k, d) for k, d in L.nodes(data=True)
         if d["bipartite"] == 0 and "tag" in d),
        key=lambda d: d[1]["tag"])
    R_boundary = sorted(
        ((k, d) for k, d in R.nodes(data=True)
         if d["bipartite"] == 0 and "tag" in d),
        key=lambda d: d[1]["tag"])
    assert len(L_boundary) == len(R_boundary)

    for i, (l, r) in enumerate(zip(L_boundary, R_boundary)):
        K.add_edge((l[0], "left"), i, key=0)
        K.add_edge(i, (r[0], "right"), key=0)
    return K
    
    # TODO check data for tags
    for l, d in L.nodes(data=True):
        if d["bipartite"] == 0:
            if L.in_degree[l] + L.out_degree[l] == 1:
                if L.in_degree[l] == 1:
                    [(y, _, z, de)] = L.in_edges(l, data=True, keys=True)
                    K.add_node(y, **d)
                    K.add_edge(y, l, z, **de)
                if L.out_degree[l] == 1:
                    [(_, y, z, de)] = L.out_edges(l, data=True, keys=True)
                    K.add_node(y, **d)
                    K.add_edge(y, l, z, **de)
    for r, d in R.nodes(data=True):
        if d["bipartite"] == 0:
            if R.in_degree[r] + R.out_degree[r] == 1:
                if R.in_degree[r] == 1:
                    [(y, _, z, de)] = R.in_edges(r, data=True, keys=True)
                    K.add_node(y, **d)
                    K.add_edge(y, r, z, **de)
                if R.out_degree[r] == 1:
                    [(_, y, z, de)] = R.out_edges(r, data=True, keys=True)
                    K.add_node(y, **d)
                    K.add_edge(y, r, z, **de)
    # for k, d in K.nodes(data=True):
    #     if d["bipartite"] == 0:
    #         assert K.in_degree[k] == 1 and K.out_degree[k] == 1
    return K
