from structlog.testing import capture_logs
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import schemas
from main import app
from store.metadata.oxigraph.store import OxigraphMetadataStore
from store.metadata.context import ContextStore
from store.csv.stub.store import StubCsvStore
from store.metadata.stub.store import StubMetadataStore

ENDPOINT = "datasets/some-dataset-id/editions/some-edition-id/versions"

def test_request_handlers_return_request_id_in_store_logs():
    """
    Confirms that:

    - Request ID is generated at the start of each request handler
    - Request ID is pass into each store method
    - All store loggers are logging with request ID
    """
    with capture_logs() as cap_logs:
        # Create a mock store with a callable mocked get_versions() method
        mock_metadata_store = MagicMock()
        # Note: returning a populated list to simulate id is found
        mock_metadata_store.get_versions = MagicMock(return_value="irrelevant")
        app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

        client = TestClient(app)
        response = client.get(ENDPOINT, headers={"Accept": "foo", "X-Request-ID": "fxa"})

        # Assertions
        for log in cap_logs:
            if 'request_id' in log:
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                assert type(log.get('request_id')) == str
                assert log.get('request_id') == "fxa"

def test_request_handlers_return_none_for_request_id_in_store_logs():
    """
    Confirms that:

    - Request ID is generated at the start of each request handler
    - Request ID is pass into each store method
    - All store loggers are logging with request ID, even if request_id=None
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
                assert type(log.get('request_id')) == type(None)
                assert log.get('request_id') == None

def test_oxigraph_get_datasets_return_request_id_in_store_log():
    """
    Confirms that:

    - Request ID is pass into store OxigraphMetadataStore methods
    - All OxigraphMetadataStore loggers are logging with request ID
    """  
    with capture_logs() as cap_logs:    
        store = OxigraphMetadataStore()
        datasets = store.get_datasets(request_id='96a101dd-c49a-4fea-aee2-a76510f32190')
        datasets_schema = schemas.Datasets(**datasets)

        for log in cap_logs:
            if log.get('event') == 'Constructing get_datasets() response from graph':
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                assert type(log.get('request_id')) == str

def test_oxigraph_get_versions_return_none_for_request_id_in_store_log():
    """
    Confirms that:

    - Request ID is pass into OxigraphMetadataStore methods
    - All OxigraphMetadataStore loggers are logging with request ID, even if request_id=None
    """ 
    with capture_logs() as cap_logs: 
        store = OxigraphMetadataStore()
        versions = store.get_versions("4gc", "2023-09", request_id=True)
        versions_schema = schemas.Versions(**versions)
        
        for log in cap_logs:
            if log.get('event') == 'Constructing get_versions() response from graph':
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                assert type(log.get('request_id')) == type(None)

def test_context_store_return_request_id_in_store_log():
    """
    Confirms that:

    - Request ID is pass into ContextStore methods
    - All ContextStore loggers are logging with request ID
    """ 
    with capture_logs() as cap_logs: 
        context_store = ContextStore()
        context = context_store.get_context(request_id='96a101dd-c49a-4fea-aee2-a76510f32190')

        for log in cap_logs:
            if log.get('event') == 'Getting Context':
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                assert type(log.get('request_id')) == str

def test_context_store_return_none_for_request_id_in_store_logs():
    """
    Confirms that:

    - Request ID is pass into ContextStore methods
    - All ContextStore loggers are logging with request ID, even if request_id=None
    """ 
    with capture_logs() as cap_logs: 
        context_store = ContextStore()
        context = context_store.get_context(request_id=None)

        for log in cap_logs:
            if log.get('event') == 'Getting Context':
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                assert type(log.get('request_id')) == type(None)

def test_csv_stub_return_request_id_in_store_log():
    """
    Confirms that:

    - Request ID is pass into StubCsvStore methods
    - All StubCsvStore loggers are logging with request ID
    """ 
    with capture_logs() as cap_logs:
        csv_store = StubCsvStore()
        csv = csv_store.get_version("cpih", "2022-01", "1", request_id='96a101dd-c49a-4fea-aee2-a76510f32190')

        for log in cap_logs:
            if log.get('event') == 'Recieved request for csv':
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                assert type(log.get('request_id')) == str

def test_csv_stub_return_none_for_request_id_in_store_log():
    """
    Confirms that:

    - Request ID is pass into StubCsvStore methods
    - All StubCsvStore loggers are logging with request ID, even if request_id=None
    """ 
    with capture_logs() as cap_logs:
        csv_store = StubCsvStore()
        csv = csv_store.get_version("cpih", "2022-01", "1", request_id=None)

        for log in cap_logs:
            if log.get('event') == 'Recieved request for csv':
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                assert type(log.get('request_id')) == type(None)

def test_stub_get_dataset_return_request_id_in_store_log():
    """
    Confirms that:

    - Request ID is pass into StubMetadataStore methods
    - All StubMetadataStore loggers are logging with request ID
    """ 

    with capture_logs() as cap_logs:
        store = StubMetadataStore()

        dataset = store.get_dataset("cpih",request_id='96a101dd-c49a-4fea-aee2-a76510f32190')

        for log in cap_logs:
            if log.get('event') == 'Constructing get_dataset() from files stored on disk':
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                assert type(log.get('request_id')) == str

def test_stub_get_datasets_return_none_for_request_id_in_store_log():
    """
    Confirms that:

    - Request ID is pass into StubMetadataStore methods
    - All StubMetadataStore loggers are logging with request ID, even if request_id=None
    """ 
   
    with capture_logs() as cap_logs:
        store = StubMetadataStore()

        datasets = store.get_datasets(request_id=None)

        for log in cap_logs:
            if log.get('event') == 'Constructing get_datasets() from files stored on disk':
                assert 'request_id' in log
                assert 'log_level' in log
                assert log.get('log_level') == 'info'
                assert type(log.get('request_id')) == type(None)