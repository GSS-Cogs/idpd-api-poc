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

    # versions = store.get_versions("4gc", "2023-09") still brings back a list
    # for versions_schema["issued"], but containing 2 different dates
    versions = store.get_versions("gdhi", "2023-03")
    versions_schema = schemas.Versions(**versions)
    
    assert len(versions_schema.versions) > 0

def test_versions_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Versions(**{"I": "break"})