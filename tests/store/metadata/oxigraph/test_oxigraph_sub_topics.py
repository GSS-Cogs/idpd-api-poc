from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_sub_topics_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_sub_topics()
    function returns a dictionary that matches the Topics schema.
    """
    store = OxigraphMetadataStore()
    sub_topics = store.get_sub_topics("economy")
    sub_topics_schema = schemas.Topics(**sub_topics)
    assert sub_topics_schema.id == "https://staging.idpd.uk/topics/economy/subtopics"
    assert sub_topics_schema.type == "hydra:Collection"
    assert len(sub_topics_schema.topics) == sub_topics_schema.count
