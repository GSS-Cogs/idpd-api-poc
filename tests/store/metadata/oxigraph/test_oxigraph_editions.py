import os
import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_editions_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_editions()
    function returns a dictionary that matches the Editions
    schema.
    """

    store = OxigraphMetadataStore()
    editions = store.get_editions("cpih")
    editions_schema = schemas.Editions(**editions)
    assert editions_schema.id == "https://staging.idpd.uk/datasets/cpih/editions"
    assert editions_schema.type == "hydra:Collection"
    assert len(editions_schema.editions) > 0


def test_editions_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Editions(**{"I": "break"})
