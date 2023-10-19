from pathlib import Path

from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from main import app, CloudStorageCsvStore

#to run tests 'unset LOCAL_BROWSE_API'
#to check responsesn in browser 'export LOCAL_BROWSE_API=true'


def test_cloud_function():
    """
     testing if the fucniton
     does download the file from the bucket
    """

    ''' # Create a mock store with a callable mocked get_version() method
    mock_csv_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_csv_store.get_version = MagicMock(return_value="")
    app.dependency_overrides[CloudStorageCsvStore] = lambda: mock_csv_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)'''

    file_response = CloudStorageCsvStore().get_version("cpih","2022-01","1")
    print(file_response)