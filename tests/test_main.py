import pytest
import json
from src.main import combine_datasets

def test_combine():
    datasets = combine_datasets()
    assert(type(datasets) == dict)
    with open("example.json","w") as f:
        json.dump(datasets,f,indent=4)
