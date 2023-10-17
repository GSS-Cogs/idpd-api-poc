import json
import pathlib
from typing import Dict


def dataset_data() -> Dict:
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_dataset().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)["datasets"][0]


def datasets_data() -> Dict:
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_datasets().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)
