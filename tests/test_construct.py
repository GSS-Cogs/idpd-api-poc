import pytest
from rdflib import URIRef
from store.metadata.sparql import construct, SPARQL_QUERIES
from store.metadata.oxigraph.store import OxigraphMetadataStore


def test_construct_query_does_not_exist():
    store = OxigraphMetadataStore()
    graph = store.db
    with pytest.raises(KeyError):
        construct(SPARQL_QUERIES["does_not_exist"], graph)


def test_construct_query_no_result():
    store = OxigraphMetadataStore()
    graph = store.db
    init_bindings = {
        "subject": URIRef(f"https://staging.idpd.uk/topics/economy"),
        "type": URIRef("http://www.w3.org/ns/dcat#theme"),
    }
    result = construct(SPARQL_QUERIES["parent_topic"], graph, init_bindings)
    # assert logger text contains "No results found for SPARQL query"
    assert len(result) == 0
