import networkx as nx

# there is a node for each combinator
# there is an edge for each pair of connected ports
# each wire is connected to zero, one or two combinators
# each combinator is connected to one wire per port

def find_all_active_wires(inet: nx.Graph):
    # find all active wires
    active = []
    for u, d in inet.nodes(data=True):
        # u is a wire
        if d["bipartite"] == 0:
            # u connects two combinators
            if len(inet[u]) == 2:
                c1, c2 = inet[u]
                # u connects two principal ports
                if inet[u][c1]["index"] == 0 and \
                    inet[u][c2]["index"] == 0:
                    active.append(u)
    return active

def annihilate_erase_erase(inet: nx.Graph):
    active = []
    for u in find_all_active_wires(inet):
        c1, c2 = inet[u]
        # erase-erase annihilation
        if inet.nodes[c1]["tag"] == "erase" and \
            inet.nodes[c2]["tag"] == "erase":
            active += [u, c1, c2]
    inet.remove_nodes_from(active)

def commute_construct_duplicate(inet: nx.Graph):
    # find all active wires
    erase = []
    for u, d in inet.nodes(data=True):
        # u is a wire
        if d["bipartite"] == 0:
            # u connects two combinators
            if len(inet[u]) == 2:
                c1, c2 = inet[u]
                # u connects two principal ports
                if inet[u][c1]["index"] == 0 and \
                    inet[u][c2]["index"] == 0:
                    tags = {"construct", "duplicate"}
                    found_tags = {inet.nodes[c1]["tag"], inet.nodes[c2]["tag"]}
                    if tags == found_tags:
                        erase += [u, c1, c2]
    inet.remove_nodes_from(erase)
    c0 = inet_add_construct(inet)
    c1 = inet_add_construct(inet)
    d0 = inet_add_duplicate(inet)
    d1 = inet_add_duplicate(inet)
    # rewire 2x2 secondary ports to 4 principals
    inet_connect_ports(inet, (c0, 0), ())
    inet_connect_ports(inet, (c1, 0), ())
    inet_connect_ports(inet, (d0, 0), ())
    inet_connect_ports(inet, (d1, 0), ())
    # wire secondary ports
    inet_connect_ports(inet, (c0, 1), (d0, 2))
    inet_connect_ports(inet, (c0, 2), (d1, 2))
    inet_connect_ports(inet, (c1, 1), (d0, 1))
    inet_connect_ports(inet, (c1, 2), (d1, 1))

def inet_add_erase(inet: nx.Graph):
    n = inet.number_of_nodes()
    inet.add_node(n, bipartite=1, tag="erase")
    inet.add_node(n+1, bipartite=0)
    inet.add_edge(n, n+1, index=0)
    return n

def inet_add_construct(inet: nx.Graph):
    n = inet.number_of_nodes()
    inet.add_node(n, bipartite=1, tag="construct")
    inet.add_node(n+1, bipartite=0)
    inet.add_node(n+2, bipartite=0)
    inet.add_node(n+3, bipartite=0)
    inet.add_edge(n, n+1, index=0)
    inet.add_edge(n, n+2, index=1)
    inet.add_edge(n, n+3, index=2)
    return n

def inet_add_duplicate(inet: nx.Graph):
    n = inet.number_of_nodes()
    inet.add_node(n, bipartite=1, tag="duplicate")
    inet.add_node(n+1, bipartite=0)
    inet.add_node(n+2, bipartite=0)
    inet.add_node(n+3, bipartite=0)
    inet.add_edge(n, n+1, index=0)
    inet.add_edge(n, n+2, index=1)
    inet.add_edge(n, n+3, index=2)
    return n

def inet_connect_ports(inet: nx.Graph, p0, p1):
    u0, i0 = p0
    u1, i1 = p1
    old_ports = []
    for _, b, i in inet.edges(u0, data="index"):
        if i == i0:
            old_ports.append(b)
    for _, b, i in inet.edges(u1, data="index"):
        if i == i1:
            old_ports.append(b)
    inet.remove_nodes_from(old_ports)
    n = inet.number_of_nodes()
    inet.add_node(n, bipartite=0)
    inet.add_edge(n, u0, index=i0)
    inet.add_edge(n, u1, index=i1)
    return n
