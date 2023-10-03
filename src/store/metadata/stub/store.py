import json
from pathlib import Path
from typing import List

from ..base import BaseMetadataStore


class StubMetadataStore(BaseMetadataStore):
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
            self.topics = json.load(f)

    def get_dataset(self, id: str) -> List[dict]:
        datasets = [x for x in self.datasets["items"] if x["identifier"] == id]
        if len(datasets) == 1:
            return datasets[0]
        return None

    def get_publisher(self, id: str) -> List[dict]:
        publishers = [x for x in self.publishers["items"] if x["identifier"] == id]
        return publishers[0] if len(publishers) == 1 else None

    def get_topic(self, id: str) -> List[dict]:
        topics = [x for x in self.topics["items"] if x["identifier"] == id]
        return topics[0] if len(topics) == 1 else None 

    def get_datasets(self) -> dict:
        return self.datasets

    def get_publishers(self) -> dict:
        return self.publishers

    def get_topics(self) -> dict:
        return self.topics
