from pathlib import Path
import json

this_dir = Path(__file__).parent
repo_root = this_dir.parent.parent

def get_dataset_json():
    """
    Returns a json response equivilent to a
    single datasets.

    i.e /datasets/{id}
    """

    file_path = Path(repo_root / "src/store/metadata/stub/content/datasets.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)["items"][0]


def get_datasets_json():
    """
    Returns a json response equivilent to many
    datasets.

    i.e /datasets/
    """
    file_path = Path(repo_root / "src/store/metadata/stub/content/datasets.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)
