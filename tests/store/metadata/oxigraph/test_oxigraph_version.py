import os
import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_version_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_version()
    function returns a version with table schema that matches the version
    schema.
    """
    store = OxigraphMetadataStore()

    version = store.get_version("cpih", "2022-01", "1")
    version_schema = schemas.VersionWithContext(**version)

    assert (
        version_schema.id
        == "https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1"
    )
    assert "dcat:Distribution" in version_schema.type
    assert "csvw:Table" in version_schema.type
    assert version_schema.identifier == "1"
    assert (
        version_schema.title
        == "Consumer Prices Index including owner occupiers' housing costs (CPIH)"
    )
    assert version_schema.issued == "2017-01-01T00:00:00"
    assert (
        version_schema.summary
        == "The Consumer Prices Index including owner occupiers' housing costs (CPIH) is a..."
    )
    assert version_schema.description == "The Consumer Prices Index..."
    assert (
        version_schema.download_url
        == "https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1.csv"
    )
    assert version_schema.media_type == "text/csv"
    assert len(version_schema.table_schema.columns) == 4

def test_version_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.VersionWithContext(**{"I": "break"})