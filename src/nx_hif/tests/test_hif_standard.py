import json
import pathlib
import pytest
from nx_hif.readwrite import read_hif, encode_hif_data

DATA_DIR = pathlib.Path(__file__).parent / "data"

def get_hif_math_model(data):
    """
    Extracts the mathematical model of the hypergraph from HIF JSON data.
    Returns a dictionary of sets/dicts representing:
    - network_type
    - metadata
    - nodes (set of IDs)
    - edges (set of IDs)
    - node_attrs (dict ID -> attrs)
    - edge_attrs (dict ID -> attrs)
    - incidences (set of frozenset/tuples representing incidences)
    """

    # 1. Network Type
    # Default is undirected
    network_type = data.get("network-type", "undirected")

    # 2. Metadata
    metadata = data.get("metadata", {})
    # Sort metadata to make it comparable if it has dicts?
    # Actually just assume equality works for dicts

    # 3. Nodes and Attributes
    # Nodes are union of explicit nodes and nodes in incidences.
    # Attributes come from explicit nodes.
    # Note: Duplicates in 'nodes' list: last one wins for attributes?
    # Or merge? NetworkX add_node updates attributes.
    # Let's assume standard behavior is last wins or merge.
    # We will simulate "sequential processing".

    nodes = set()
    node_attrs = {}

    # Process explicit nodes
    for n_record in data.get("nodes", []):
        nid = n_record["node"]
        nodes.add(nid)
        if "attrs" in n_record:
            # We assume attributes are merged or overwritten.
            # Let's use simple overwrite for canonical model for now,
            # unless we find we need merge.
            if nid not in node_attrs:
                node_attrs[nid] = {}
            node_attrs[nid].update(n_record["attrs"])
        if "weight" in n_record:
             if nid not in node_attrs:
                node_attrs[nid] = {}
             node_attrs[nid]["weight"] = n_record["weight"]

    # 4. Edges and Attributes
    edges = set()
    edge_attrs = {}

    for e_record in data.get("edges", []):
        eid = e_record["edge"]
        edges.add(eid)
        if "attrs" in e_record:
            if eid not in edge_attrs:
                edge_attrs[eid] = {}
            edge_attrs[eid].update(e_record["attrs"])
        if "weight" in e_record:
             if eid not in edge_attrs:
                edge_attrs[eid] = {}
             edge_attrs[eid]["weight"] = e_record["weight"]

    # 5. Incidences
    # List of records.
    # Each record: edge, node, optional weight, optional direction, optional attrs.
    # We need a canonical representation.
    # We can use a frozenset of items for the record, but dict is not hashable.
    # We'll use a tuple of sorted items.

    incidences = []

    for i_record in data.get("incidences", []):
        eid = i_record["edge"]
        nid = i_record["node"]

        # Add to sets
        nodes.add(nid)
        edges.add(eid)

        # Build incidence object
        inc_obj = {
            "edge": eid,
            "node": nid
        }

        # Attributes
        if "attrs" in i_record:
            inc_obj["attrs"] = i_record["attrs"]

        # Weight
        if "weight" in i_record:
            # Store weight in attrs for comparison uniformity or keep separate?
            # HIF schema has weight as top-level optional in incidence.
            inc_obj["weight"] = i_record["weight"]

        # Direction
        # If network is undirected, direction is irrelevant?
        # Or should we enforce "head"?
        # The paper says: "When using the 'directed' keyword, this indicates that the library should expect the 'direction' field"
        # "When the network type is not specified, it is assumed that the type is an undirected hypergraph."
        # If undirected, direction should be ignored or effectively "head" (default).
        # My encoder strips direction if it is "head".
        # So we should normalize direction to "head" if missing.
        # And if network is undirected, maybe we force it to "head"?
        # Let's normalize: if missing, set to "head".

        d = i_record.get("direction", "head")
        if network_type == "directed":
            inc_obj["direction"] = d
        else:
            # Undirected: ignore direction, or assume it's meaningless.
            # But if input has it, and output doesn't...
            # Mathematical definition of undirected hypergraph doesn't have direction.
            # So we should NOT include it in the math model for undirected.
            pass

        # Convert attrs dict to frozenset of items for hashability
        if "attrs" in inc_obj:
            inc_obj["attrs"] = frozenset(sorted(inc_obj["attrs"].items()))

        # Convert to tuple of sorted items
        inc_tuple = tuple(sorted(inc_obj.items()))
        incidences.append(inc_tuple)

    # We use a Counter (multiset) for incidences because duplicate incidences might be allowed?
    # Schema doesn't forbid it.
    # However, standard sets usually suffice if we assume unique incidences.
    # Let's use sorted list for comparison to handle duplicates if any.
    incidences.sort(key=str)

    return {
        "network_type": network_type,
        "metadata": metadata,
        "nodes": nodes,
        "edges": edges,
        "node_attrs": node_attrs,
        "edge_attrs": edge_attrs,
        "incidences": incidences
    }

def compare_hif_math_models(input_data, output_data):
    m1 = get_hif_math_model(input_data)
    m2 = get_hif_math_model(output_data)

    # Compare
    assert m1["network_type"] == m2["network_type"]
    assert m1["metadata"] == m2["metadata"]
    assert m1["nodes"] == m2["nodes"]
    assert m1["edges"] == m2["edges"]
    assert m1["node_attrs"] == m2["node_attrs"]
    assert m1["edge_attrs"] == m2["edge_attrs"]
    assert m1["incidences"] == m2["incidences"]

@pytest.mark.parametrize("json_file", DATA_DIR.glob("*.json"))
def test_hif_compliance(json_file):
    with open(json_file) as f:
        input_data = json.load(f)

    G = read_hif(json_file)
    output_data = encode_hif_data(G)

    try:
        compare_hif_math_models(input_data, output_data)
    except AssertionError:
        print(f"\nFailed file: {json_file.name}")
        # print(f"Input: {json.dumps(input_data, indent=2)}")
        # print(f"Output: {json.dumps(output_data, indent=2)}")
        raise
