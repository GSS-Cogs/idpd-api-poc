import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_topics_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_topics()
    function returns a list of topics that matches the Topics
    schema.
    """
    store = OxigraphMetadataStore()
    topics = store.get_topics()
    topics_schema = schemas.Topics(**topics)
    topic_ids = {topic.id for topic in topics_schema.topics}
    assert topics_schema.id == "https://staging.idpd.uk/topics"
    assert topics_schema.type == "hydra:Collection"
    assert len(topics_schema.topics) == 2
    assert topic_ids == {
        "https://staging.idpd.uk/topics/prices",
        "https://staging.idpd.uk/topics/economy",
    }


def test_topics_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Topics(**{"I": "break"})
