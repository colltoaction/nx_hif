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
import networkx as nx


def dpo_rewrite(G: nx.MultiDiGraph, L: nx.MultiDiGraph, R: nx.MultiDiGraph, K: nx.MultiDiGraph):
    """
    To rewrite 𝐺 into 𝐻 we compute the object 𝐶 for the
    pushout complement 𝐾 −→ 𝐶 −→ 𝐺 of 𝐾 −→ 𝐿 −𝑚→ 𝐺.
    𝐶 holds the part of 𝐺 that isn't matched by 𝑚,
    so we form the the span 𝐶 ←− 𝐾 −→ 𝑅,
    and obtain 𝐻 as the pushout.
    """
    (L, L_boundary) = L
    (R, R_boundary) = R
    # we first relabel to simplify further transformations
    G = nx.convert_node_labels_to_integers(G)
    # TODO remove from boundary
    L_sub = nx.MultiDiGraph(L)
    L_sub.remove_nodes_from(
        x[0][0] for y, yd in K.nodes(data=True)
        if yd["bipartite"] == 0
        for x in K.out_edges(y, keys=True, data=True))
    R_sub = nx.MultiDiGraph(R)
    R_sub.remove_nodes_from(
        x[1][0] for y, yd in K.nodes(data=True)
        if yd["bipartite"] == 0
        for x in K.in_edges(y, keys=True, data=True))

    matcher = nx.isomorphism.MultiDiGraphMatcher(
        G, L_sub,
        lambda n1, n2:
            n1["bipartite"] == n2["bipartite"] == 0 or
            (n1["bipartite"] == n2["bipartite"] == 1 and n1["tag"] == n2["tag"]),
        lambda _a, _b: True)

    # for each of those edges, after removing the iso,
    # we connect C_inner to R_sub.
    # but the iso doesn't give an ordering.
    C = nx.MultiDiGraph(G)
    for iso in matcher.subgraph_isomorphisms_iter():
        n = C.number_of_nodes()
        # shift all R ids by n
        R_mapping = {r: r+n for r in R_sub.nodes()}
        R_sub = nx.relabel_nodes(R_sub, R_mapping)
        C.update(R_sub)

        # TODO use L_boundary
        # K embeds into L and R using their boundaries
        assert len(K.in_edges) == len(K.out_edges) == 2*len(L_boundary.edges) == 2*len(R_boundary.edges)
        for i in range(len(L_boundary.edges)):
            wire_boundary_i = i
            # a boundary wire has exactly one edge.
            # the other end is a box with port.
            # that is part of the isomorphic subgraph,
            # TODO K edges must store some key. lk?
            [((left_wire, _), _, lk, _)] = K.in_edges(wire_boundary_i, keys=True, data=True)
            [(_, (right_wire, _), rk, _)] = K.out_edges(wire_boundary_i, keys=True, data=True)

            # for each left_wire we have
            # one edge to the iso subgraph.
            # since the iso will be replaced by R_sub
            # we must replicate that in R
            c_iso_i = None
            for l_iso, c_iso in iso.items():
                if L.has_edge(l_iso, left_wire, lk):
                    assert not c_iso_i
                    c_iso_i = c_iso
                elif L.has_edge(left_wire, l_iso, lk):
                    assert not c_iso_i
                    c_iso_i = c_iso
            assert c_iso_i is not None
            # TODO
            # From c_iso_i we traverse out to find the inner boundary c_bound_i.
            # Since c_iso_i might have many edges (even to the same wire, in a loop)
            # we find the one corresponding to this particular left_wire.
            # we identify it by the key (port number)
            # if there are more than one.

            # we reattach c_bound_i to the box in r_sub
            # the edge key is taken from the right_wire edge in R.
            # r is the other end of the same-index boundary wire in R
            # TODO use rk to disambiguate when there are more than one,
            # otherwise assert it matches
            c_bound_i = None
            # keys are unique across c_iso_i in-out edges
            for a, _, c_iso_i_k, d in C.in_edges(c_iso_i, keys=True, data=True):
                # check if this corresponds to left_wire
                if c_iso_i_k == lk:
                    assert not c_bound_i
                    c_bound_i = a
            for _, a, c_iso_i_k, d in C.out_edges(c_iso_i, keys=True, data=True):
                # check if this corresponds to left_wire
                if c_iso_i_k == lk:
                    assert not c_bound_i
                    c_bound_i = a
            assert c_bound_i is not None

            if R.in_degree[right_wire] == 1:
                [(r_sub_i, _, k, d)] = R.in_edges(right_wire, keys=True, data=True)
                # shift
                r_sub_i += n
                C.add_edge(r_sub_i, c_bound_i, k, **d)
            elif R.out_degree[right_wire] == 1:
                [(_, r_sub_i, k, d)] = R.out_edges(right_wire, keys=True, data=True)
                # shift
                r_sub_i += n
                C.add_edge(c_bound_i, r_sub_i, k, **d)
            else:
                # if 0
                assert False
        C.remove_nodes_from(iso.keys())
    return C

def dpo_invariant(C, L, R):
    """
    The invariant subgraph 𝐾 is upgraded from a discrete hypergraph
    consisting of the inputs and the outputs of the two sides of the rule,
    to a mapping between L and R boundary nodes.
    """
    K = nx.MultiDiGraph()
    (L, L_boundary) = L
    (R, R_boundary) = R
    assert len(L_boundary.edges) == len(R_boundary.edges)

    for i, e in enumerate(L_boundary.edges):
        # TODO edges might have keys or not
        # because there might be isolated wires
        # connected to the boundary.
        # 
        (l, ) = L_boundary[i]
        ld = L.nodes[l]
        (r, ) = R_boundary[i]
        rd = R.nodes[r]
        K.add_node(i, bipartite=1)
        K.add_node((l, "left"), **ld)
        K.add_node((r, "right"), **rd)
        kl_edge = ()
        kr_edge = ()
        for e in L.in_edges(l, keys=True, data=True):
            # assert not kl_edge
            K.add_edge((l, "left"), i, e[2])
        for e in L.out_edges(l, keys=True, data=True):
            # assert not kl_edge
            K.add_edge((l, "left"), i, e[2])
        for e in R.in_edges(r, keys=True, data=True):
            # assert not kr_edge
            K.add_edge(i, (r, "right"), e[2])
        for e in R.out_edges(r, keys=True, data=True):
            # assert not kr_edge
            K.add_edge(i, (r, "right"), e[2])
        # assert kl_edge
        # assert kr_edge
        # TODO add port index as key
        # coming from the edge key, from the boundary to the internal wire.
        # it must restore the original information.
        # (_, _, lk, _) = 
        # (_, _, rk, _) = 
    return K
