import json
from pathlib import Path
from typing import Dict

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

        with open(Path(content_dir / "editions.json").absolute()) as f:
            self.editions = json.load(f)

        with open(Path(content_dir / "publishers.json").absolute()) as f:
            self.publishers = json.load(f)

        with open(Path(content_dir / "topics.json").absolute()) as f:
            self.topics = json.load(f)

    def get_datasets(self) -> Dict:
        return self.datasets

    def get_dataset(self, id: str) -> Dict:
        dataset = next(
            (x for x in self.datasets["items"] if x["identifier"] == id), None
        )
        return dataset

    def get_editions(self) -> Dict:
        return self.editions

    def get_edition(self, id: str) -> Dict:
        edition = next(
            (
                x
                for x in self.editions["items"]
                if x["items"]["in_series"].endswith(id) == id
            ),
            None,
        )
        return edition
    
    def get_versions(self, dataset_id: str, edition_id: str) -> Dict:
        raise NotImplementedError

    def get_version(self, dataset_id: str, edition_id: str, version_id: str) -> Dict:
        raise NotImplementedError

    def get_publishers(self) -> Dict:
        return self.publishers

    def get_publisher(self, publisher_id: str) -> Dict:
        raise NotImplementedError

    def get_topics(self) -> Dict:
        return self.topics

    def get_topic(self, topic_id: str) -> Dict:
        raise NotImplementedError

    def get_sub_topics(self, topic_id: str) -> Dict:
        raise NotImplementedError

    def get_sub_topic(self, topic_id: str, sub_topic_id: str) -> Dict:
        raise NotImplementedError