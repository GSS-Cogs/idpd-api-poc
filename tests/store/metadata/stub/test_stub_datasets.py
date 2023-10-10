import pytest

from pydantic import ValidationError

from store.metadata.stub.store import StubMetadataStore
from src import schemas


def test_stub_get_datasets_returns_valid_structure():
    """
    Confirm that the OxigrapgMetadataStore.get_dataset()
    function returns a dataset that matches the dataset
    schema.
    """

    store = StubMetadataStore()
    
    datasets = store.get_datasets()
    
    # Sanity check that the schema validation is working as intended
    # i.e raises with wrong structure
    with pytest.raises(ValidationError):
        schemas.Datasets(**{"I": "break"})

    # So should not raise
    schemas.Datasets(**datasets)