import os
import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_edition_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_edition()
    function returns an edition that matches the edition
    schema.
    """

    store = OxigraphMetadataStore()

    edition = store.get_edition("cpih", "2022-01")
    edition_schema = schemas.Edition(**edition)

    assert edition_schema.id == "https://staging.idpd.uk/datasets/cpih/editions/2022-01"
    assert edition_schema.type == "dcat:Dataset"
    assert edition_schema.description == "The Consumer Prices Index..."
    assert edition_schema.identifier == "2022-01"
    assert len(edition_schema.table_schema.columns) == 4


def test_edition_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Edition(**{"I": "break"})
