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
    sparql_queries = OxigraphMetadataStore().sparql_queries
    init_bindings = {
        "subject": URIRef(f"https://staging.idpd.uk/topics/economy"),
        "type": URIRef("http://www.w3.org/ns/dcat#theme"),
    }
    result = sparql_queries.parent_topic(init_bindings)
    assert len(result) == 0


def test_invalid_subject_init_binding():
    sparql_queries = OxigraphMetadataStore().sparql_queries
    init_bindings = {
        "subject": "http://www.example.org",
        "type": "http://www.w3.org/ns/dcat#DatasetSeries",
    }
    result = sparql_queries.dataset(init_bindings)
    assert result == None


def test_invalid_type_init_binding():
    sparql_queries = OxigraphMetadataStore().sparql_queries
    init_bindings = {
        "subject": "https://staging.idpd.uk/datasets/cpih",
        "type": "invalid-type",
    }
    result = sparql_queries.dataset(init_bindings)
    assert result == None
