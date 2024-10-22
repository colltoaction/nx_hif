# HIF for NetworkX

The Hypergraph Interchange Format implementation makes NetworkX compatible with several higher-order graph networks using an equivalence with graphs as explained in nLab:
* https://github.com/pszufe/HIF-standard
* https://github.com/networkx/networkx
* https://ncatlab.org/nlab/show/hypergraph#hypergraphs_as_2colored_graphs

Python Projects participating in HIF standarization:
* [HypergraphX](https://github.com/HGX-Team/hypergraphx) (Python)
* [HyperNetX](https://github.com/pnnl/HyperNetX) (Python)
* [XGI](https://github.com/xgi-org/xgi) (Python)

## Formal interchange with NetworkX

As seen in the nLab entry, one can go back and forth between 2-colored graph and hypergraph representations. This allows libraries to delegate low-level operations to NetworkX, focusing on higher-order algorithms over a robust Python library.
