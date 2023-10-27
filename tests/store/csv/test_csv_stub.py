from starlette.responses import FileResponse

from store.csv.stub.store import StubCsvStore


def test_csv_stub_instantiation():
    """
    Just test the store can be instantiationed
    i.e it implements the correct methods.
    """
    StubCsvStore()


def test_csv_stub_returns_csv_without_file_extentions():
    """
    Just test the store can return a csv when we
    ask for a csv that we know exists but dont include
    the ".csv" file extensions.
    """
    csv_store = StubCsvStore()
    assert isinstance(csv_store.get_version("cpih", "2022-01", "1.csv"), FileResponse)


def test_csv_stub_returns_csv_with_file_extentions():
    """
    Just test the store can return a csv when we
    ask for a csv that we know exists and we do include
    the ".csv" file extension.
    """
    csv_store = StubCsvStore()
    assert isinstance(csv_store.get_version("cpih", "2022-01", "1"), FileResponse)


def test_csv_stub_returns_none():
    """
    Just test the store can return None when we
    ask for a csv that we know does not exist
    """
    csv_store = StubCsvStore()
    assert csv_store.get_version("foo", "bar", "baz") is None
