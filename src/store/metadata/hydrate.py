from typing import Dict, List


def hydrate(data, sub_graphs_dict: Dict):
    """
    To be used recursively. Populates the contents of the data object by
    accounting for its type, modifying data if necessary (if it is a dictionary
    that does not have valid keys/values or if it is a list) then recalling
    itself until data population is complete.
    """

    if isinstance(data, dict):
        if "@id" in data.keys() and "@type" not in data.keys():
            data = sub_graphs_dict.get(data["@id"], data)
        else:
            for k, v in data.items():
                data[k] = hydrate(v, sub_graphs_dict)

    elif isinstance(data, list):
        for i, v in enumerate(data):
            data[i] = hydrate(v, sub_graphs_dict)

    elif isinstance(data, str):
        data = sub_graphs_dict.get(data, data)

    return data


def _hydrate_graph_from_sub_graphs(graph: Dict, sub_graphs: List[Dict]) -> Dict:
    """
    Parses the main graph to find any @id's that are references to
    other graphs and populates the sub documents from them.
    """

    sub_graphs_list = [x for x in sub_graphs if x != graph]

    sub_graphs_dict = {sub_graph["@id"]: sub_graph for sub_graph in sub_graphs_list}

    for sub_graph_dict in sub_graphs_dict.values():
        # Drop any @id fields that signify an anonamous nodes

        if sub_graph_dict["@id"].startswith("bnode:"):
            del sub_graph_dict["@id"]

    graph = hydrate(graph, sub_graphs_dict)
    if "table_schema" in graph:
        graph["table_schema"] = hydrate(graph["table_schema"])

    return graph