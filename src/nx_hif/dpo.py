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
        # TODO edge key/port check
        lambda _a, _b: True)

    # for each of those edges, after removing the iso,
    # we connect C_inner to R_sub.
    # but the iso doesn't give an ordering.
    C = nx.MultiDiGraph(G)
    c_bound_remove = {}
    for iso in matcher.subgraph_isomorphisms_iter():
        n = C.number_of_nodes()
        # shift all R ids by n
        R_mapping = {r: r+n for r in R_sub.nodes()}
        R_sub = nx.relabel_nodes(R_sub, R_mapping)
        C.update(
            R_sub.edges(keys=True, data=True),
            R_sub.nodes(data=True))

        for i in range(len(L_boundary.edges)):
            wire_boundary_i = i
            [((left_wire, _), _, lk, _)] = K.in_edges(wire_boundary_i, keys=True, data=True)
            [(_, (right_wire, _), rk, _)] = K.out_edges(wire_boundary_i, keys=True, data=True)

            # for each left_wire we have
            # one edge to the iso subgraph.
            # since the iso will be replaced by R_sub
            # we must replicate that in R
            c_iso_i = None
            for c_iso, l_iso in iso.items():
                if L.has_edge(l_iso, left_wire, lk):
                    assert not c_iso_i
                    c_iso_i = c_iso
                elif L.has_edge(left_wire, l_iso, lk):
                    assert not c_iso_i
                    c_iso_i = c_iso
            if c_iso_i is None:
                assert False
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
            for a, _, c_iso_i_k, d in G.in_edges(c_iso_i, keys=True, data=True):
                # check if this corresponds to left_wire
                if c_iso_i_k == lk:
                    assert not c_bound_i
                    c_bound_i = a
            for _, a, c_iso_i_k, d in G.out_edges(c_iso_i, keys=True, data=True):
                # check if this corresponds to left_wire
                if c_iso_i_k == lk:
                    assert not c_bound_i
                    c_bound_i = a
            # TODO think swap
            # if c_bound_i is None:
            #     assert False
            # assert c_bound_i is not None

            # TODO three cases
            # 1. 0 edges is passthrough L to R
            # 2. 1 edge L to C
            # 3. 1 edge C to R
            # for (r_sub_i, _, k, d) in R.in_edges(right_wire, keys=True, data=True):
            #     # shift
            #     r_sub_i += n
            #     print("addin", r_sub_i, c_bound_i, k, rk, d)
            #     C.add_edge(r_sub_i, c_bound_i, k, **d)
            # for (_, r_sub_i, k, d) in R.out_edges(right_wire, keys=True, data=True):
            #     # shift
            #     r_sub_i += n
            #     print("addout", c_bound_i, r_sub_i, k, d)
            #     C.add_edge(c_bound_i, r_sub_i, k, **d)
            # for e in R_boundary.in_edges(right_wire, keys=True, data=True):
            #     print("R_boundary.in_edges", e)
            #     # C.add_edge(i, (right_wire, "right"), key=e[2])


            if R.in_degree[right_wire] == 1:
                [(r_sub_i, _, k, d)] = R.in_edges(right_wire, keys=True, data=True)
                # shift
                r_sub_i += n
                print("addin", r_sub_i, c_bound_i, k, rk, lk, d)
                C.add_edge(r_sub_i, c_bound_i, lk, **d)
            elif R.out_degree[right_wire] == 1:
                [(_, r_sub_i, k, d)] = R.out_edges(right_wire, keys=True, data=True)
                # shift
                r_sub_i += n
                print("addout", c_bound_i, r_sub_i, k, d)
                C.add_edge(c_bound_i, r_sub_i, lk, **d)
            else:
                assert R.in_degree[right_wire] == R.out_degree[right_wire] == 0
                assert len(R_boundary.in_edges(right_wire, keys=True, data=True)) == 2
                if c_bound_i is not None:
                    # contract wires c_bound_i and r
                    print(iso)
                    # print(c_bound_i, C.nodes[c_bound_i])
                    for a, _, k, d in G.in_edges(c_bound_i, keys=True, data=True):
                        print(a, k, d)
                        C.add_edge(a, right_wire, k, **d)
                    for _, a, k, d in G.out_edges(c_bound_i, keys=True, data=True):
                        print(a, k, d)
                        C.add_edge(right_wire, a, k, **d)
                    # isos will be removed later
                    c_bound_remove[c_bound_i] = right_wire
                    # C.remove_node(c_bound_i)
                    # print(R_boundary.in_edges(wire_boundary_i, keys=True, data=True))
                    # print(R_boundary.out_edges(wire_boundary_i, keys=True, data=True))
                    # print(c_iso_i, C.nodes[c_iso_i])
                    # print(C.in_edges(c_iso_i, keys=True, data=True))
                    # print(C.out_edges(c_iso_i, keys=True, data=True))
                    # assert False
                # TODO consider R_boundary because
                # 
        C.remove_nodes_from(iso.keys())
    C.remove_nodes_from(c_bound_remove.keys())
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
        (l, ) = L_boundary[i]
        ld = L.nodes[l]
        (r, ) = R_boundary[i]
        rd = R.nodes[r]
        K.add_node(i, bipartite=1)
        K.add_node((l, "left"), **ld)
        K.add_node((r, "right"), **rd)
        for e in L.in_edges(l, keys=True, data=True):
            K.add_edge((l, "left"), i, key=e[2])
        for e in L.out_edges(l, keys=True, data=True):
            K.add_edge((l, "left"), i, key=e[2])
        # TODO think swap
        # for e in L_boundary.out_edges(l, keys=True, data=True):
        #     K.add_edge((l, "left"), i, key=e[2])
        # R has two isolated nodes
        # with links from two R_boundary nodes.
        # in this case they exist in K
        # but are not associated with an index node.
        # since we are still interested in their
        # connections, we have to find them in the boundary
        for e in R.in_edges(r, keys=True, data=True):
            K.add_edge(i, (r, "right"), key=e[2])
        for e in R.out_edges(r, keys=True, data=True):
            K.add_edge(i, (r, "right"), key=e[2])
        # TODO this might do over work
        for e in R_boundary.out_edges(r, keys=True, data=True):
            K.add_edge(i, (r, "right"), key=e[2])
    return K
