import pytest
import json
import os

from pydantic import ValidationError

from store.metadata.stub.store import StubMetadataStore, combine_datasets
from src import schemas


def test_stub_get_datasets_returns_valid_structure():
    """
    Confirm that the StubMetadataStore.get_dataset()
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


def test_combine_datsets():
    """
    Confirms the amalgamation of datasets works as 
    intended, with all checks passing and no exceptions raised
    """
    datasets = combine_datasets()
    assert(type(datasets) == dict)
    assert datasets["@context"] == "https://staging.idpd.uk/ns#"
    assert datasets["@type"] == [
        "dcat:Catalog",
        "hydra:Collection"
    ]
    assert datasets["@id"] == "https://staging.idpd.uk/datasets"
    assert len(datasets["datasets"]) > 0
    assert datasets["count"] > 0
    
    with open("example.json","w") as f:
        json.dump(datasets,f,indent=4)


def test_none_dataset_files_dont_affect_dataset_amalgamation():
    """
    Should any other non json files exist under thae 
    'src/store/metadata/stub/content/datasets/' directory, then the 
    dataset amalgamation function should still pass with correct results
    """
    with open('src/store/metadata/stub/content/datasets/example.txt', 'w') as f:
        f.write('first line')
    datasets = combine_datasets()
    assert(type(datasets) == dict)
    assert datasets["@context"] == "https://staging.idpd.uk/ns#"
    assert datasets["@type"] == [
        "dcat:Catalog",
        "hydra:Collection"
    ]
    assert datasets["@id"] == "https://staging.idpd.uk/datasets"
    assert len(datasets["datasets"]) > 0
    assert datasets["count"] > 0

    DATASETS_DIR = "src/store/metadata/stub/content/datasets"
    file_count = 0
    for file in os.listdir(DATASETS_DIR):
        file_path = os.path.join(DATASETS_DIR, file)
        if os.path.isfile(file_path):
            file_count += 1

    assert len(datasets["datasets"]) < file_count
    os. remove("src/store/metadata/stub/content/datasets/example.txt")

