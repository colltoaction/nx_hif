import networkx as nx

# there is a node for each combinator
# there is an edge for each pair of connected ports
# each wire is connected to zero, one or two combinators
# each combinator is connected to one wire per port

def annihilate_erase_erase(inet: nx.Graph):
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
                    # erase-erase annihilation
                    if inet.nodes[c1]["tag"] == "erase" and \
                        inet.nodes[c2]["tag"] == "erase":
                        erase.append(u)
    for u in erase:
        c1, c2 = inet[u]
        inet.remove_node(u)
        inet.remove_node(c1)
        inet.remove_node(c2)
