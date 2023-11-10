import pytest

from pydantic import ValidationError

from store.metadata.oxigraph.store import OxigraphMetadataStore
import schemas


def test_oxigraph_get_datasets_returns_valid_structure():
    """
    Confirm that the OxigraphMetadataStore.get_datasets()
    function returns a list of datasets that matches the Datasets
    schema.
    """
    store = OxigraphMetadataStore()
    datasets = store.get_datasets()
    datasets_schema = schemas.Datasets(**datasets)
    dataset_ids = {dataset.id for dataset in datasets_schema.datasets}
    assert datasets_schema.id == "https://staging.idpd.uk/datasets"
    assert datasets_schema.type == "hydra:Collection"
    assert len(datasets_schema.datasets) == 2
    assert dataset_ids == {
        "https://staging.idpd.uk/datasets/prices",
        "https://staging.idpd.uk/datasets/economy",
    }


def test_datasets_schema_validation():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.datasets(**{"I": "break"})
