import json
from pathlib import Path
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
from store.metadata.context import ContextStore
import schemas
from starlette.responses import FileResponse

from store.csv.stub.store import StubCsvStore

from store.metadata.stub.store import StubMetadataStore
from src import schemas

ENDPOINT = "datasets/some-dataset-id/editions/some-edition-id/versions"

def test_request_handlers_return_logger_request_id():
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
                assert type(log.get('request_id')) == str

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

def test_oxigraph_get_versions_logger_request_id_is_none():
    """
    Confirm that the OxigraphMetadataStore.get_versions()
    function returns a dictionary that matches the Versions
    schema.
    """
    with capture_logs() as cap_logs: 
        store = OxigraphMetadataStore()
        versions = store.get_versions("4gc", "2023-09", request_id=None)
        versions_schema = schemas.Versions(**versions)
        
        for log in cap_logs:
            # if 'request_id' in log:
            assert 'request_id' in log
            assert 'log_level' in log
            assert log.get('log_level') == 'info'
            # assert type(log.get('request_id')) == None

def test_context_store_logger_returns_request_id():
    with capture_logs() as cap_logs: 
        context_store = ContextStore()
        context = context_store.get_context(request_id=3)

        for log in cap_logs:
                # if 'request_id' in log:
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                # assert type(log.get('request_id')) == None

def test_context_store_logger_request_id_is_none():
    with capture_logs() as cap_logs: 
        context_store = ContextStore()
        context = context_store.get_context(request_id=None)

        for log in cap_logs:
                # if 'request_id' in log:
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                # assert type(log.get('request_id')) == None

def test_csv_stub_logger_returns_request_id():
    """
    Just test the store can return a csv when we
    ask for a csv that we know exists but do include
    the ".csv" file extensions.
    """
    with capture_logs() as cap_logs:
        csv_store = StubCsvStore()
        csv = csv_store.get_version(request_id=3)

        for log in cap_logs:
                # if 'request_id' in log:
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                # assert type(log.get('request_id')) == None

def test_csv_stub_logger_request_id_is_none():
    """
    Just test the store can return a csv when we
    ask for a csv that we know exists but do include
    the ".csv" file extensions.
    """
    with capture_logs() as cap_logs:
        csv_store = StubCsvStore()
        csv = csv_store.get_version(request_id=None)

        for log in cap_logs:
                # if 'request_id' in log:
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                # assert type(log.get('request_id')) == None

def test_stub_get_dataset_logger_returns_request_id():
    """
    Confirm that the OxigrapgMetadataStore.get_dataset()
    function returns a dataset that matches the dataset
    schema.
    """

    with capture_logs() as cap_logs:
        store = StubMetadataStore()

        dataset = store.get_dataset("cpih",request_id=3)

        for log in cap_logs:
                # if 'request_id' in log:
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                # assert type(log.get('request_id')) == None

def test_stub_get_datasets_logger_request_id_is_none():
    """
    Confirm that the OxigrapgMetadataStore.get_dataset()
    function returns a dataset that matches the dataset
    schema.
    """

    with capture_logs() as cap_logs:
        store = StubMetadataStore()

        datasets = store.get_datasets(request_id=None)

        for log in cap_logs:
                # if 'request_id' in log:
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                # assert type(log.get('request_id')) == None