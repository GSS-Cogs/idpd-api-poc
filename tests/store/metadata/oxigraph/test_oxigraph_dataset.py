import os
import pytest

from pydantic import ValidationError

from src.store.metadata.oxigraph.store import OxigraphMetadataStore
from src import schemas


def test_oxigraph_get_dataset_returns_valid_structure():
    """
    Confirm that the OxigrapgMetadataStore.get_dataset()
    function returns a dataset that matches the dataset
    schema.
    """

    os.environ["GRAPH_DB_URL"] = "http://localhost:7878"
    store = OxigraphMetadataStore()
    
    dataset = store.get_dataset("cpih")
    
    # Sanity check that the schema validation is working as intended
    # i.e raises with wrong structure
    with pytest.raises(ValidationError):
        schemas.Dataset(**{"I": "break"})

    # So should not raise
    schemas.Dataset(**dataset)