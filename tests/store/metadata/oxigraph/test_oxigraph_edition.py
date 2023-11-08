import os
import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_edition_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_edition()
    function returns an edition that matches the edition
    schema.
    """

    store = OxigraphMetadataStore()

    edition = store.get_edition("cpih", "2022-01")
    edition_schema = schemas.Edition(**edition)

    assert isinstance(edition_schema.contact_point, schemas.ContactPoint)
    assert edition_schema.contact_point.email == "mailto:cpih@ons.gov.uk"
    assert edition_schema.contact_point.name == "Consumer Price Inflation Enquiries"
    assert edition_schema.creator == "office-for-national-statistics"
    assert edition_schema.description == "The Consumer Prices Index..."
    assert edition_schema.frequency.name == "monthly"
    assert edition_schema.frequency.value == "monthly"
    assert isinstance(edition_schema.frequency, schemas.Frequency)
    assert edition_schema.id == "https://staging.idpd.uk/datasets/cpih/editions/2022-01"
    assert edition_schema.identifier == "2022-01"
    assert edition_schema.in_series == "https://staging.idpd.uk/datasets/cpih"
    assert edition_schema.issued == "2017-02-21T09:30:00+00:00"
    assert set(edition_schema.keywords) == {"consumer price index", "CPIH", "inflation"}
    assert (
        edition_schema.licence
        == "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
    )
    assert edition_schema.modified == "2017-02-21T09:30:00+00:00"
    assert edition_schema.next_release == "2017-03-11T09:30:00+00:00"
    assert (
        edition_schema.publisher
        == "https://staging.idpd.uk/office-for-national-statistics"
    )
    assert edition_schema.spatial_coverage == "E92000001"
    assert set(edition_schema.spatial_resolution) == {"E01", "E92"}
    assert (
        edition_schema.summary
        == "The Consumer Prices Index including owner occupiers' housing costs (CPIH) is a..."
    )
    assert len(edition_schema.table_schema.columns) == 3
    assert isinstance(edition_schema.temporal_coverage, schemas.PeriodOfTime)
    assert edition_schema.temporal_coverage.start == "1981-01-01T00:00:00+00:00"
    assert edition_schema.temporal_coverage.end == "2022-01-31T00:00:00+00:00"
    assert set(edition_schema.temporal_resolution) == {"P1Y", "P1M", "P3M"}
    assert (
        edition_schema.title
        == "Consumer Prices Index including owner occupiers' housing costs (CPIH)"
    )
    assert edition_schema.topics[0] == "https://staging.idpd.uk/topics/economy"
    assert edition_schema.type == "dcat:Dataset"
    assert (
        edition_schema.versions[0]
        == "https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1"
    )
    assert (
        edition_schema.versions_url
        == "https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions"
    )
    assert True


def test_edition_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Edition(**{"I": "break"})
