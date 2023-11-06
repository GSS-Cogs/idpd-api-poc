import os
import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_version_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_topic()
    function returns a topic with sub_topic that matches the topic
    schema.
    """

    os.environ["GRAPH_DB_URL"] = "http://localhost:7878"
    store = OxigraphMetadataStore()

    version = store.get_version(dataset_id="?", edition_id="?", version_id="economy")
    version_schema = schemas.Version(**version)
    
    # id: str = Field(alias="@id")
    # assert version_schema.id == "https://staging.idpd.uk/topics/economy"
    assert version_schema.id == "http://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}"
    
    # type: List[str] = Field(alias="@type")
    assert version_schema.type == "dcat:theme"

    # identifier: str
    assert version_schema.identifier == "economy"

    # title: str = Field(max_length=90)
    assert version_schema.title == "Economy"
    
    # issued: str = Field(
    #     pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
    # )
    assert version_schema.issued == ""
    
    # summary: str = Field(max_length=200)
    assert version_schema.summary == ""

    # description: str = Field(max_length=250)
    assert version_schema.description == ""

    # download_url: str
    assert version_schema.download_url == ""

    # media_type: str
    assert version_schema.media_type == ""

    # table_schema: TableSchema
    assert version_schema.table_schema == ""