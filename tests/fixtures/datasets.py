import json
import pathlib
import pytest

from src.store.metadata.stub.store import combine_datasets

@pytest.fixture
def dataset_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_dataset().
    """
    dataset = combine_datasets()["datasets"][0]
    dataset["@context"] = "https://staging.idpd.uk/ns#"
    return dataset


@pytest.fixture
def datasets_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_datasets().
    """
    return combine_datasets()
