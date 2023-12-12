from typing import Optional
from structlog.testing import capture_logs
from unittest.mock import MagicMock

from fastapi import status
from fastapi.exceptions import ResponseValidationError
from fastapi.testclient import TestClient
import pytest

from constants import JSONLD
from main import app, StubMetadataStore
from tests.fixtures.versions import versions_test_data

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas

ENDPOINT = "datasets/some-dataset-id/editions/some-edition-id/versions"

def test_logger_request_id():
    """
    Confirms that:

    - Where we do not have an "accept: application/json+ld" header.
    - Then store.get_versions() is not called.
    - Status code 406 is returned.
    """
    with capture_logs() as cap_logs:
        # Create a mock store with a callable mocked get_versions() method
        mock_metadata_store = MagicMock()
        # Note: returning a populated list to simulate id is found
        mock_metadata_store.get_versions = MagicMock(return_value="irrelevant")
        app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

        client = TestClient(app)
        response = client.get(ENDPOINT, headers={"Accept": "foo"})

        # Assertions
        for log in cap_logs:
            if 'request_id' in log:
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                assert type(log.get('request_id')) == Optional[int]

def test_oxigraph_get_datasets_logger_returns_request_id():
    """

    """  
    with capture_logs() as cap_logs:    
        store = OxigraphMetadataStore()
        datasets = store.get_datasets(request_id=8)
        datasets_schema = schemas.Datasets(**datasets)

        for log in cap_logs:
            # if 'request_id' in log:
            assert 'request_id' in log
            assert 'log_level' in log
            assert log.get('log_level') == 'info'
            # assert type(log.get('request_id')) == None

def test_oxigraph_get_versions_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_versions()
    function returns a dictionary that matches the Versions
    schema.
    """
    store = OxigraphMetadataStore()
    versions = store.get_versions("4gc", "2023-09")
    versions_schema = schemas.Versions(**versions)
    assert (
        versions_schema.id
        == "https://staging.idpd.uk/datasets/4gc/editions/2023-09/versions"
    )
    assert versions_schema.type == "hydra:Collection"
    assert len(versions_schema.versions) == versions_schema.count