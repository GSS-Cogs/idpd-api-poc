from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_sub_topics_returns_valid_structure():
    store = OxigraphMetadataStore()

    topics = store.get_topics()
    sub_topics = store.get_sub_topics("economy")
    topic_schema = schemas.Topic(**sub_topics)
    assert True
