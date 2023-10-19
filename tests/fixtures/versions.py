import json
import pathlib


def versions_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_versions().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/editions/versions/cpih_2022-01.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)
