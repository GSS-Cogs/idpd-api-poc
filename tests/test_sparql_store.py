from typing import Dict
import pytest

from store.sparql import SparqlStore


def test_run_sparql():
    """testing that the get_dataset will return access
    the url provided and run the SPRQL query, returns a Dictionary"""

    fornow = SparqlStore()

    result = fornow.get_datasets()

    assert isinstance(result, Dict)
