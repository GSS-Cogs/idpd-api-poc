import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_topics_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_topics()
    function returns a dictionary that matches the Topics
    schema.
    """
    store = OxigraphMetadataStore()
    topics = store.get_topics()
    topics_schema = schemas.Topics(**topics)
    assert topics_schema.id == "https://staging.idpd.uk/topics"
    assert topics_schema.type == "hydra:Collection"
    assert len(topics_schema.topics) == topics_schema.count


def test_topics_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Topics(**{"I": "break"})
