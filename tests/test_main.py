import glob
import pytest
import json
from src.store.metadata.stub.store import combine_datasets
from src.data import populate

def test_combine():
    datasets = combine_datasets()
    assert(type(datasets) == dict)
    with open("example.json","w") as f:
        json.dump(datasets,f,indent=4)

def test_make_populate():
    populate("http://localhost:7878")