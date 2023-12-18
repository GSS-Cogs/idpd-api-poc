import re
import json
import pathlib
import pytest

from rdflib import Graph, URIRef
from store.metadata.hydrate import _hydrate_graph_from_sub_graphs
from pyld import jsonld

from src.store.metadata import constants
from src.store.metadata.oxigraph.store import OxigraphMetadataStore, _get_single_graph_for_field

# from tests.fixtures.datasets import dataset_test_data

# ENDPOINT = "/datasets/some-id"

# def test_hydrate_graph_from_subgraphs(dataset_test_data):
#     mock_metadata_store = MagicMock()
#     mock_metadata_store.hydrate_graph_from_subgraphs = MagicMock(return_value=dataset_test_data)
#     app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

#     # Create a TestClient for your FastAPI app
#     client = TestClient(app)
#     response = client.get(ENDPOINT, headers={"Accept": JSONLD})

#     # Assertions
#     assert response.status_code == status.HTTP_200_OK
#     mock_metadata_store.hydrate_graph_from_subgraphs.assert_called_once()


# file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
# with open(file_path, "r") as json_file:
#     dataset = json.load(json_file)["datasets"][0]
# dataset["@context"] = "https://staging.idpd.uk/ns#"
# test_graph_dict = dataset

# A different attempt using oxigraph implementation

def _populate_partial_graph_for_test():
    """
    Partial implementation of oxigraph `get_dataset` method to 
    give a list of graphs to use as input for tests, without 
    completing the flattening/embedding process.
    """

    # Make a dictionary to use as input
    store = OxigraphMetadataStore()
    #dataset = store.get_dataset("cpih")

    #hydrated_dataset = _hydrate_graph_from_sub_graphs(dataset, )

    # Define initBindings for SPARQL query
    init_bindings = {
        "subject": URIRef(f"https://staging.idpd.uk/datasets/cpih"),
        "type": URIRef("http://www.w3.org/ns/dcat#DatasetSeries"),
    }

    # Extract RDF triples from the database as one Graph
    # TODO: incorporate `keywords` and `topics` into the `sparql_queries.dataset` query?
    result: Graph = (
        store.sparql_queries.dataset(init_bindings)
        + store.sparql_queries.keywords(init_bindings)
        + store.sparql_queries.topic_uris(init_bindings)
        + store.sparql_queries.contact_point(init_bindings)
        + store.sparql_queries.temporal_coverage(init_bindings)
        + store.sparql_queries.editions(init_bindings)
    )

    # Serialize the graph into jsonld
    data = json.loads(result.serialize(format="json-ld"))

    # Use a context file to shape our jsonld, removing long form references
    data = jsonld.flatten(
        data, {"@context": constants.CONTEXT, "@type": "dcat:DatasetSeries"}
    )

    # Extract dataset graph and blank node graphs from flattened json-ld data
    dataset_graph = _get_single_graph_for_field(data, "@type")
    contact_point_graph = _get_single_graph_for_field(data, "vcard:fn")
    temporal_coverage_graph = _get_single_graph_for_field(data, "dcat:endDate")
    if None in [dataset_graph, contact_point_graph, temporal_coverage_graph]:
        return None

    # Add `issued` and `modified` fields to each edition in `editions`
    edition_graphs = [
        x
        for x in data["@graph"]
        if "@id" in x.keys() and re.search("/editions/", x["@id"])
    ]
    dataset_graph["editions"] = edition_graphs

    del dataset_graph["versions"]

    # dataset_graph = {"@context": "https://staging.idpd.uk/ns#", **dataset_graph}

    all_graphs_list = [dataset_graph, contact_point_graph, temporal_coverage_graph]
    
    return all_graphs_list

def test_hydrate_graph_from_subgraphs():

    test_graphs = _populate_partial_graph_for_test()
    main_graph = test_graphs[0]

    hydrated_graph = _hydrate_graph_from_sub_graphs(main_graph, test_graphs)

    assert hydrated_graph
