import os
import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_topic_with_subtopic_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_topic()
    function returns a dictionary with subtopic that matches the Topic schema.
    """
    store = OxigraphMetadataStore()
    topic = store.get_topic("economy")
    topic_schema = schemas.Topic(**topic)
    assert topic_schema.id == "https://staging.idpd.uk/topics/economy"
    assert topic_schema.type == "dcat:theme"
    assert "https://staging.idpd.uk/topics/prices" in topic_schema.sub_topics


def test_oxigraph_get_topic_with_context_and_subtopic_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_topic()
    function returns a dictionary with subtopic that matches the TopicWithContext schema.
    """
    store = OxigraphMetadataStore()
    topic = store.get_topic("economy")
    topic_schema = schemas.TopicWithContext(**topic)
    assert topic_schema.id == "https://staging.idpd.uk/topics/economy"
    assert topic_schema.type == "dcat:theme"
    assert "https://staging.idpd.uk/topics/prices" in topic_schema.sub_topics
    assert topic_schema.context == "https://staging.idpd.uk/ns#"


def test_oxigraph_get_topic_with_parent_topic_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_topic()
    function returns a dictionary with parent topic that matches the Topic schema.
    """
    store = OxigraphMetadataStore()
    topic = store.get_topic("prices")
    topic_schema = schemas.Topic(**topic)
    assert topic_schema.id == "https://staging.idpd.uk/topics/prices"
    assert topic_schema.type == "dcat:theme"
    assert "https://staging.idpd.uk/topics/economy" in topic_schema.parent_topics


def test_oxigraph_get_topic_with_context_and_parent_topic_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_topic()
    function returns a dictionary with parent topic that matches the TopicWithContext schema.
    """
    store = OxigraphMetadataStore()
    topic = store.get_topic("prices")
    topic_schema = schemas.TopicWithContext(**topic)
    assert topic_schema.id == "https://staging.idpd.uk/topics/prices"
    assert topic_schema.type == "dcat:theme"
    assert "https://staging.idpd.uk/topics/economy" in topic_schema.parent_topics
    assert topic_schema.context == "https://staging.idpd.uk/ns#"


def test_topic_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Topic(**{"I": "break"})
