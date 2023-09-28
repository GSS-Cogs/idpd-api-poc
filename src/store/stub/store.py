import json
import csv
from pathlib import Path
from typing import List

from fastapi.responses import FileResponse
from store.base import BaseStore, BaseCsvStore

class StubStore(BaseStore):
    """
    A stub of a store that returns representative metadata from
    files stored on disk.
    """

    def setup(self):
        """
        Populates our in memory stubbed responses
        using the contents of ./content
        """
        content_dir = Path(Path(__file__).parent / "content")

        with open(Path(content_dir / "datasets.json").absolute()) as f:
            self.datasets = json.load(f)

        with open(Path(content_dir / "publishers.json").absolute()) as f:
            self.publishers = json.load(f)

        with open(Path(content_dir / "topics.json").absolute()) as f:
            self.themes = json.load(f)

    def get_dataset_by_id(self, id: str) -> List[dict]:
        return [x for x in self.datasets["items"] if x["id"] == id]

    def get_publisher_by_id(self, id: str) -> List[dict]:
        return [x for x in self.publishers["items"] if x["id"] == id]
    
    def get_topic_by_id(self, id: str) -> List[dict]:
        return [x for x in self.themes["items"] if x["id"] == id]
    
    def get_datasets(self) -> dict:
        return self.datasets

    def get_publishers(self) -> dict:
        return self.publishers
    
    def get_topics(self) -> dict:
        return self.themes


class StubMetadataStore(BaseCsvStore):
    """
    A stub of a store that returns representative csv from
    files stored on disk.
    """
    def setup(self):
        self.datasets = {}

        content_dir = Path(Path(__file__).parent / "csv/cipd/2022-3")

        with open(Path(content_dir / "dataset.csv").absolute()) as f:
            self.datasets["dataset"] = csv.reader(f)
        
        with open(Path(content_dir / "dummy2.csv").absolute()) as f:
            self.datasets["dummy2"] = csv.reader(f)

        with open(Path(content_dir / "dummy3.csv").absolute()) as f:
            self.datasets["dummy3"] = csv.reader(f)

    def get_version(self, dataset_id: str, edition_id: str, version_id: str):
        adress = f"{dataset_id}/{edition_id}/{version_id}"
        return FileResponse(self.datasets[adress])