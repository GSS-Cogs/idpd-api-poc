import pytest
from typing import AsyncGenerator

import asyncio

import store.csv.googlecloudstorage.store as csvstore
from store.csv.googlecloudstorage.store import CloudStorageCsvStore

# Dev Note:
# We don't want to be calling GCP to test as its an external
# dependency, so we're monkey patching some responses in
# order to test the CloudStorageCsvStore logic in isolation.

@pytest.fixture
def monkeypath_file_stream_working(monkeypatch):
    """
    Monkey patch _file stream so it returns a tiny async generator
    rather than actually interacting with GCP.
    """
    async def mock_file_stream(_):
        for i in range(0, 2):
            yield i
            await asyncio.sleep(1)  

    monkeypatch.setattr(csvstore, "_file_stream", mock_file_stream)
    yield mock_file_stream
    monkeypatch.undo()

@pytest.fixture
def monkeypath_download_does_not_exist(monkeypatch):
    """
    Monkey patch download_exists() to simulate the store
    being asked to download a file that does not exist
    on GCP.
    """
    def download_exists(_):
        return False  

    monkeypatch.setattr(csvstore, "download_exists", download_exists)
    yield download_exists
    monkeypatch.undo()


def test_download_csv_googlecloudstorage_returns_success(monkeypath_file_stream_working):
    """
    Test that we can download a csv from google cloud
    storage as intended.
    """

    store = CloudStorageCsvStore()
    # Note: check_exists=False otherwise it'll reach out to GCP which we don't
    # want our tests to be doing.
    filename, file_stream = store.get_version("gdhi", "2023-03", "1", check_exists=False)

    assert filename == "gdhi_2023-03_1.csv"
    assert isinstance(file_stream, AsyncGenerator)


def test_download_csv_googlecloudstorage_returns_failure(monkeypath_download_does_not_exist):
    """
    Test that where a file does not exist the store
    has a controlled failure.
    """

    store = CloudStorageCsvStore()
    filename, file_stream = store.get_version("gdhi", "2023-03", "1")

    assert filename is None
    assert file_stream is None
