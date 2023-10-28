import json
import os
from pathlib import Path
from typing import Dict

from ..base import BaseMetadataStore


def recursive_replace(data, find, replace):
    """
    Recursively replace specific values with value
    fields of a dictionary.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                recursive_replace(value, find, replace)
            elif isinstance(value, str):
                data[key] = value.replace(find, replace)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                recursive_replace(item, find, replace)
            elif isinstance(item, str):
                data[i] = item.replace(find, replace)


def contextualise(resource) -> Dict:
    """
    Add an appropriate context field.

    Where specified by an env var replace the host path
    as it appears in value fields.
    """
    if resource is None:
        return None

    if "@context" not in resource.keys():
        resource = {"@context": "https://staging.idpd.uk/#ns"} | resource

    replace_host = os.environ.get("LOCAL_BROWSE_API", None)
    if replace_host is not None:
        recursive_replace(resource, "https://staging.idpd.uk", "http://localhost:8000")
    return resource


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

        # TODO - grep the whole folder for editions json's, use dataset_id and
        # edition_id as key in data holding dict
        with open(Path(content_dir / "editions/cpih_2022-01.json").absolute()) as f:
            self.editions = {"cpih_2022-01": json.load(f)}

        # TODO - grep the whole folder for editions json's, use dataset_id and
        # edition_id as key in data holding dict
        with open(
            Path(content_dir / "editions/versions/cpih_2022-01.json").absolute()
        ) as f:
            self.versions = {"cpih_2022-01": json.load(f)}

        with open(Path(content_dir / "publishers.json").absolute()) as f:
            self.publishers = json.load(f)

        with open(Path(content_dir / "topics.json").absolute()) as f:
            self.topics = json.load(f)

    def get_datasets(self) -> Dict:
        return contextualise(self.datasets)

    def get_dataset(self, id: str) -> Dict:
        dataset = next(
            (x for x in self.datasets["datasets"] if x["identifier"] == id), None
        )
        return contextualise(dataset)

    def get_editions(self, dataset_id: str) -> Dict:
        all_edition_keys = self.editions.keys()
        edition_key = next(
            (x for x in all_edition_keys if x.split("_")[0] == dataset_id),
            None,
        )
        return contextualise(self.editions.get(edition_key, None))

    def get_edition(self, dataset_id: str, edition_id: str) -> Dict:
        editions_for_dataset = self.get_editions(dataset_id)
        if editions_for_dataset is None:
            return None
        edition = next(
            (
                x
                for x in editions_for_dataset["editions"]
                if x["identifier"] == edition_id
            ),
            None,
        )
        return contextualise(edition)

    def get_versions(self, dataset_id: str, edition_id: str) -> Dict:
        all_version_keys = self.versions.keys()
        version_key = next(
            (x for x in all_version_keys if x == f"{dataset_id}_{edition_id}"),
            None,
        )
        return contextualise(self.versions.get(version_key, None))

    def get_version(self, dataset_id: str, edition_id: str, version_id: str) -> Dict:
        versions_for_dataset = self.get_versions(dataset_id, edition_id)
        if versions_for_dataset is None:
            return None
        edition = next(
            (
                x
                for x in versions_for_dataset["versions"]
                if x["identifier"] == version_id
            ),
            None,
        )
        return contextualise(edition)

    def get_publishers(self) -> Dict:
        return contextualise(self.publishers)

    def get_publisher(self, publisher_id: str) -> Dict:
        publishers = self.get_publishers()
        if publishers is None:
            return None
        return contextualise(
            next(
                (
                    x
                    for x in publishers["publishers"]
                    if x["@id"].endswith(publisher_id)
                ),
                None,
            )
        )

    def get_topics(self) -> Dict:
        return contextualise(self.topics)

    def get_topic(self, topic_id: str) -> Dict:
        topics = self.get_topics()
        if topics is None:
            return None
        return contextualise(
            next(
                (x for x in topics["topics"] if x["identifier"].endswith(topic_id)),
                None,
            )
        )

    def get_sub_topics(self, topic_id: str) -> Dict:
        topic = self.get_topic(topic_id)
        if topic is None:
            return None

        sub_topic_ids = topic["sub_topics"]
        topics = self.get_topics()
        sub_topics = [x for x in topics if x["@id"] in sub_topic_ids]

        if sub_topics is None:
            return None
        return contextualise(
            {
                "items": sub_topics,
                "count": len(sub_topics),
                "offset": 0,
            }
        )

    def get_sub_topic(self, topic_id: str, sub_topic_id: str) -> Dict:
        raise NotImplementedError
