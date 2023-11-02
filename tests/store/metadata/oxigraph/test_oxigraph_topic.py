import os
import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_topic_with_subtopic_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_topic()
    function returns a topic with sub_topic that matches the topic
    schema.
    """

    os.environ["GRAPH_DB_URL"] = "http://localhost:7878"
    store = OxigraphMetadataStore()

    topic = store.get_topic("economy")
    topic_schema = schemas.Topic(**topic)

    assert topic_schema.id == "https://staging.idpd.uk/topics/economy"
    assert topic_schema.type == "dcat:theme"
    assert topic_schema.identifier == "economy"
    assert topic_schema.title == "Economy"
    assert topic_schema.sub_topics[0] == "https://staging.idpd.uk/topics/prices"


def test_oxigraph_get_topic_with_parent_topic_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_topic()
    function returns a topic with parent topic that matches the topic
    schema.
    """
    os.environ["GRAPH_DB_URL"] = "http://localhost:7878"
    store = OxigraphMetadataStore()

    topic = store.get_topic("prices")
    topic_schema = schemas.Topic(**topic)

    assert topic_schema.id == "https://staging.idpd.uk/topics/prices"
    assert topic_schema.type == "dcat:theme"
    assert topic_schema.identifier == "prices"
    assert topic_schema.title == "Prices"
    assert topic_schema.parent_topics[0] == "https://staging.idpd.uk/topics/economy"


def test_topic_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Topic(**{"I": "break"})
