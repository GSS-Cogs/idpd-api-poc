import os
import pytest

from pydantic import ValidationError

from src.store.metadata.oxigraph.store import OxigraphMetadataStore
from src import schemas

# TODO - reimplenet as part of graph work

def test_oxigraph_get_dataset_returns_valid_structure():
#     """
#     Confirm that the OxigrapgMetadataStore.get_dataset()
#     function returns a dataset that matches the dataset
#     schema.
#     """

    os.environ["GRAPH_DB_URL"] = "http://localhost:7878"
    store = OxigraphMetadataStore()

    edition = store.get_edition("cpih")

    # TODO: look at query results to write assertions
    assert