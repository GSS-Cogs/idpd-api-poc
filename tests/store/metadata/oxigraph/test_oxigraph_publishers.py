import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_publishers_valid_return():
    """
    Confirm that the OxigraphMetadataStore.get_publishers()
    function returns a list of publishers that matches the Publishers
    schema.
    """

    store = OxigraphMetadataStore()
    publishers = store.get_publishers()
    publishers_schema = schemas.Publishers(**publishers)
    assert publishers_schema.id == "https://staging.idpd.uk/publishers"
    assert publishers_schema.type == "hydra:Collection"


def test_topics_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Publishers(**{"I": "break"})