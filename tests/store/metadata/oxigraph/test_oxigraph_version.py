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

    version = store.get_version(dataset_id="cpih", edition_id="2022-01", version_id="1")
    version_schema = schemas.Version(**version)
    
    assert version_schema.id == "https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1"
    assert "dcat:Distribution" in version_schema.type
    assert "csvw:Table" in version_schema.type
    assert version_schema.identifier == "1"
    assert version_schema.title == "Consumer Prices Index including owner occupiers' housing costs (CPIH)"
    assert version_schema.issued == "2017-01-01T00:00:00"
    assert version_schema.summary == "he Consumer Prices Index including owner occupiers' housing costs (CPIH) is a..."
    assert version_schema.description == "The Consumer Prices Index..."
    assert version_schema.download_url == "https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1.csv"
    # assert version_schema.media_type == "text/csv"
    assert version_schema.table_schema == {
                "columns": [
                    {
                    "name": "geography",
                    "datatype": "string",
                    "titles": "Geography",
                    "description": "The geography associated with the observation."
                    },
                    {
                    "name": "time_period",
                    "datatype": "string",
                    "titles": "Time period",
                    "description": "The time period associated with the observation."
                    },
                    {
                    "name": "cpih",
                    "datatype": "number",
                    "titles": "Consumer price index",
                    "description": "The consumer price index for the given time period."
                    }
                ]
            }