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
        Populates our in-memory stubbed responses
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

    def get_editions(self, dataset_id: str) -> Dict:
        editions_for_dataset = [
            x for x in self.editions["items"] if x["in_series"].endswith(dataset_id)]
        if editions_for_dataset is not None:
            return {
            "items": editions_for_dataset,
            "count": len(editions_for_dataset),
            "offset": 0
        }
        return None

    def get_edition(self, dataset_id: str, edition_id: str) -> Dict:
        editions_for_dataset = self.get_editions(dataset_id)
        if editions_for_dataset is None:
            return None
        edition = next(
            (
                x
                for x in editions_for_dataset["items"]
                if x["identifier"] == edition_id
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
