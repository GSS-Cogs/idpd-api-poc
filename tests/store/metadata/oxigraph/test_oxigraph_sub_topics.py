from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_sub_topics_returns_valid_structure():
    store = OxigraphMetadataStore()

    sub_topics = store.get_sub_topics("economy")
    sub_topics_schema = schemas.Topics(**sub_topics)
    assert sub_topics_schema.id == "https://staging.idpd.uk/topics/economy/subtopics"
    assert len(sub_topics_schema.topics) > 0
    assert sub_topics_schema.topics[0].id == "https://staging.idpd.uk/topics/prices"
