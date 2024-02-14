import pytest

from pydantic import ValidationError

from store.metadata.stub.stub_store import StubMetadataStore
from src import schemas


def test_stub_get_dataset_returns_valid_structure():
    """
    Confirm that the StubMetadataStore.get_dataset()
    function returns a dataset that matches the dataset
    schema.
    """

    store = StubMetadataStore()

    dataset = store.get_dataset("cpih")

    # Sanity check that the schema validation is working as intended
    # i.e raises with wrong structure
    with pytest.raises(ValidationError):
        schemas.Dataset(**{"I": "break"})

    # So should not raise
    schemas.Dataset(**dataset)
