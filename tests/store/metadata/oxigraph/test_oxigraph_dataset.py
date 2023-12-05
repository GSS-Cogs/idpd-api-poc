import os
import pytest

from pydantic import ValidationError

from src.store.metadata.oxigraph.store import OxigraphMetadataStore
from src import schemas


def test_oxigraph_get_dataset_returns_valid_structure():
    """
    Confirm that the OxigrapgMetadataStore.get_dataset()
    function returns a dictionary that matches the Dataset
    schema.
    """
    store = OxigraphMetadataStore()
    dataset = store.get_dataset("cpih")
    dataset_schema = schemas.Dataset(**dataset)
    assert dataset_schema.id == "https://staging.idpd.uk/datasets/cpih"
    assert dataset_schema.type == "dcat:DatasetSeries"


def test_oxigraph_get_dataset_with_context_returns_valid_structure():
    """
    Confirm that the OxigrapgMetadataStore.get_dataset()
    function returns a dictionary that matches the DatasetWithContext schema.
    """
    store = OxigraphMetadataStore()
    dataset = store.get_dataset("cpih")
    dataset_schema = schemas.DatasetWithContext(**dataset)
    assert dataset_schema.id == "https://staging.idpd.uk/datasets/cpih"
    assert dataset_schema.type == "dcat:DatasetSeries"
    assert dataset_schema.context == "https://staging.idpd.uk/ns#"


def test_oxigraph_get_dataset_returns_invalid_structure():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.Dataset(**{"I": "break"})


def test_oxigraph_get_dataset_with_context_returns_invalid_structure():
    """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
    with pytest.raises(ValidationError):
        schemas.DatasetWithContext(**{"I": "break"})
