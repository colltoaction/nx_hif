import networkx as nx
from inet import annihilate_erase_erase


def test_annihilate_erase_erase():
    inet = nx.Graph()
    inet.add_node(1, bipartite=0)
    inet.add_node(2, bipartite=1, tag="erase")
    inet.add_node(3, bipartite=1, tag="erase")
    inet.add_edge(1, 2, index=0)
    inet.add_edge(1, 3, index=0)

    annihilate_erase_erase(inet)
    assert len(inet) == 0
