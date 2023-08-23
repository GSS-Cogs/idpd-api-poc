import pytest

from store.sparql import SparqlStore
from SPARQLWrapper import QueryResult


def test_get_datasets():
    """testing that the get_dataset will return access
    the url provided and run the SPRQL query, returns a QueryResult object"""

    fornow = SparqlStore()

    result = fornow.get_datasets()

    assert isinstance(result, QueryResult)
