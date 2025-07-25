import networkx as nx

# there is a node for each combinator
# there is a node for each wire, including disconnected wires
# there is an edge for each pair of connected ports
# each wire is connected to one or two combinators
# each combinator is connected to one wire per port
# a loop or self-connection uses multiedges for each port

def find_all_active_wires(inet: nx.MultiGraph):
    # find all active wires
    active = []
    for u, d in inet.nodes(data=True):
        # u is a wire
        if d["bipartite"] == 0:
            # u connects two combinators
            if len(inet[u]) == 2:
                c1, c2 = inet[u]
                # u connects two principal ports at index 0
                if c1 != c2 and \
                    0 in inet[u][c1] and \
                    0 in inet[u][c2]:
                    active.append((u, c1, c2))
    return active

def annihilate_erase_erase(inet: nx.MultiGraph):
    active = []
    for u, c1, c2 in find_all_active_wires(inet):
        if inet.nodes[c1]["tag"] == "erase" and \
            inet.nodes[c2]["tag"] == "erase":
            active.append([u, c1, 0])
            active.append([u, c2, 0])
    inet.remove_edges_from(active)

def commute_construct_duplicate(inet: nx.MultiGraph):
    active = []
    for u, c, d in find_all_active_wires(inet):
        tags = {"construct", "duplicate"}
        found_tags = {inet.nodes[c]["tag"], inet.nodes[d]["tag"]}
        if tags == found_tags:
            active.append((u, c, d))

    for u, c, d in active:
        c0 = inet_add_construct(inet)
        c1 = inet_add_construct(inet)
        d0 = inet_add_duplicate(inet)
        d1 = inet_add_duplicate(inet)
        # rewire 2x2 secondary ports to 4 principals
        inet_connect_ports(inet, (c0, 0), (d, 2))
        inet_connect_ports(inet, (c1, 0), (d, 1))
        inet_connect_ports(inet, (d0, 0), (c, 1))
        inet_connect_ports(inet, (d1, 0), (c, 2))
        inet.remove_edges_from(list(inet.edges(c)))
        inet.remove_edges_from(list(inet.edges(d)))
        # wire secondary ports
        inet_connect_ports(inet, (c0, 1), (d0, 2))
        inet_connect_ports(inet, (c0, 2), (d1, 2))
        inet_connect_ports(inet, (c1, 1), (d0, 1))
        inet_connect_ports(inet, (c1, 2), (d1, 1))

def inet_add_erase(inet: nx.MultiGraph):
    n = inet.number_of_nodes()
    inet.add_node(n, bipartite=1, tag="erase")
    inet.add_node(n+1, bipartite=0)
    inet.add_edge(n, n+1, key=0)
    return n

def inet_add_construct(inet: nx.MultiGraph):
    n = inet.number_of_nodes()
    inet.add_node(n, bipartite=1, tag="construct")
    inet.add_node(n+1, bipartite=0)
    inet.add_node(n+2, bipartite=0)
    inet.add_node(n+3, bipartite=0)
    inet.add_edge(n, n+1, key=0)
    inet.add_edge(n, n+2, key=1)
    inet.add_edge(n, n+3, key=2)
    return n

def inet_add_duplicate(inet: nx.MultiGraph):
    n = inet.number_of_nodes()
    inet.add_node(n, bipartite=1, tag="duplicate")
    inet.add_node(n+1, bipartite=0)
    inet.add_node(n+2, bipartite=0)
    inet.add_node(n+3, bipartite=0)
    inet.add_edge(n, n+1, key=0)
    inet.add_edge(n, n+2, key=1)
    inet.add_edge(n, n+3, key=2)
    return n

def inet_find_wire(inet: nx.MultiGraph, u, i):
    for w0, w1, j in inet.edges(u, keys=True):
        if i == j:
            return w1 if u == w0 else w0
    assert False

def inet_connect_ports(inet: nx.MultiGraph, p0, p1):
    u0, i0 = p0
    u1, i1 = p1
    w0 = inet_find_wire(inet, u0, i0)
    w1 = inet_find_wire(inet, u1, i1)
    inet.remove_edge(u0, w0)
    inet.remove_edge(u1, w1)
    w = inet.number_of_nodes()
    inet.add_node(w, bipartite=0)
    inet.add_edge(w, u0, key=i0)
    inet.add_edge(w, u1, key=i1)
    return w
