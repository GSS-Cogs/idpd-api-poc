import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_versions_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_versions()
    function returns a versions that matches the Versions
    schema.
    """
    store = OxigraphMetadataStore()

    versions = store.get_versions("4gc", "2023-09")
    versions_schema = schemas.Versions(**versions)
    assert versions_schema.context == "https://staging.idpd.uk/ns#"
    assert versions_schema.id == "https://staging.idpd.uk/datasets/4gc/editions/2023-09/versions"
    assert versions_schema.type == "hydra:Collection"
    assert versions_schema.title == "4G Coverage"
    assert len(versions_schema.versions) > 0
    assert versions_schema.count == 1
    assert versions_schema.offset == 0

def test_versions_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Versions(**{"I": "break"})