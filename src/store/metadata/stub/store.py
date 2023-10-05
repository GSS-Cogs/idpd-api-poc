import json
from pathlib import Path
from typing import Optional, Dict

from ..base import BaseMetadataStore


class StubMetadataStore(BaseMetadataStore):
    """
    A stub of a store that returns representative metadata from
    files stored on disk.
    """

    def setup(self):
        """
        Populates our in-memory stubbed responses
        using the contents of ./content
        """
        content_dir = Path(Path(__file__).parent / "content")

        with open(Path(content_dir / "datasets.json").absolute()) as f:
            self.datasets = json.load(f)

        with open(Path(content_dir / "publishers.json").absolute()) as f:
            self.publishers = json.load(f)

        with open(Path(content_dir / "topics.json").absolute()) as f:
            self.topics = json.load(f)

    def get_dataset(self, id: str) -> Optional[Dict]:
        dataset = next((x for x in self.datasets["items"] if x["identifier"] == id), None)
        return dataset

    def get_publisher(self, id: str) -> Optional[Dict]:
        publisher = next((x for x in self.publishers["items"] if x["identifier"] == id), None)
        return publisher

    def get_topic(self, id: str) -> Optional[Dict]:
        topic = next((x for x in self.topics["items"] if x["identifier"] == id), None)
        return topic

    def get_datasets(self) -> Dict:
        return self.datasets

    def get_publishers(self) -> Dict:
        return self.publishers

    def get_topics(self) -> Dict:
        return self.topics
