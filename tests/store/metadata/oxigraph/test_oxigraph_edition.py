import os
import pytest

from pydantic import ValidationError

from src.store.metadata.oxigraph.store import OxigraphMetadataStore
from src import schemas

def test_oxigraph_get_edition_returns_valid_structure():
#     """
#     Confirm that the OxigrapgMetadataStore.get_edition()
#     function returns an edition that matches the edition
#     schema.
#     """

    os.environ["GRAPH_DB_URL"] = "http://localhost:7878"
    store = OxigraphMetadataStore()

    edition = store.get_edition("cpih", "2022-01")
    edition_schema = schemas.Edition(**edition)

    # TODO: Once the query construct/get functions are fully working, look at query results to write assertions
    assert edition_schema