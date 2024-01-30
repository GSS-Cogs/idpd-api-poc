import glob
import json
import os
from pathlib import Path
from typing import Dict, Optional

from ..base import BaseMetadataStore

# from main import combine_datasets
from custom_logging import logger , configure_logger

configure_logger()


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
        resource = {"@context": "https://staging.idpd.uk/ns#"} | resource

    replace_host = os.environ.get("LOCAL_BROWSE_API", None)
    if replace_host is not None:
        recursive_replace(resource, "https://staging.idpd.uk", "http://localhost:8000")
    return resource

def combine_datasets()-> dict:
    DATASETS_DIR = "src/store/metadata/stub/content/datasets"
    dataset = {}
    for file in os.listdir(DATASETS_DIR):
        file_path = os.path.join(DATASETS_DIR, file)
        if os.path.isfile(file_path):
            with open(file_path) as json_file:
                if not dataset:
                    dataset = json.load(json_file)
                    dataset['datasets'] = dataset.pop('dataset')
                else:
                    sub_datasets = json.load(json_file)
                    for key in sub_datasets:
                        if key == "datasets":
                            sub_dataset = sub_datasets[key][0]
                            dataset[key].append(sub_dataset)
    dataset['count'] = len(dataset["datasets"])

    # api won't start if datasets checks fail
    if len(dataset["datasets"]) != len(os.listdir(DATASETS_DIR)):
        raise Exception("Number of dataset definitions don't match number of datset files.")

    return dataset


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

        # get specific stubbed resources into memory on application startup
        # with open(Path(content_dir / "datasets.json").absolute()) as f:
        #     self.datasets = json.load(f)
        self.datasets = combine_datasets()

        with open(Path(content_dir / "publishers.json").absolute()) as f:
            self.publishers = json.load(f)

        with open(Path(content_dir / "topics.json").absolute()) as f:
            self.topics = json.load(f)

        # for editions and versions we glob the directories in question
        # and scoop up all jsons. We use the naming conventions of
        # <dataset_id>_<edition_id> to populate the keys so we can get
        # them back out
        editions_dir = Path(content_dir / "datasets" / "editions")
        self.editions = {}
        for edition_json_file in glob.glob(os.path.join(editions_dir, "*.json")):
            with open(edition_json_file) as f:
                self.editions[
                    edition_json_file.split("/")[-1].rstrip(".json")
                ] = json.load(f)

        versions_dir = Path(editions_dir /"versions")
        self.versions = {}
        for version_json_file in glob.glob(os.path.join(versions_dir, "*.json")):
            with open(version_json_file) as f:
                self.versions[
                    version_json_file.split("/")[-1].rstrip(".json")
                ] = json.load(f)

    def get_datasets(self, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_datasets() from files stored on disk", request_id=request_id)
        return contextualise(self.datasets)

    def get_dataset(self, id: str, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_dataset() from files stored on disk", request_id=request_id)
        dataset = next(
            (x for x in self.datasets["datasets"] if x["identifier"] == id), None
        )
        return contextualise(dataset)

    def get_editions(self, dataset_id: str, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_editions() from files stored on disk", request_id=request_id)
        all_edition_keys = self.editions.keys()
        edition_key = next(
            (x for x in all_edition_keys if x.split("_")[0] == dataset_id),
            None,
        )
        return contextualise(self.editions.get(edition_key, None))

    def get_edition(self, dataset_id: str, edition_id: str, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_edition() from files stored on disk", request_id=request_id)
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

    def get_versions(self, dataset_id: str, edition_id: str, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_versions() from files stored on disk", request_id=request_id)
        all_version_keys = self.versions.keys()
        version_key = next(
            (x for x in all_version_keys if x == f"{dataset_id}_{edition_id}"),
            None,
        )
        return contextualise(self.versions.get(version_key, None))

    def get_version(self, dataset_id: str, edition_id: str, version_id: str, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_version() from files stored on disk", request_id=request_id)
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

    def get_publishers(self, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_publishers() from files stored on disk", request_id=request_id)
        return contextualise(self.publishers)

    def get_publisher(self, publisher_id: str, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_publisher() from files stored on disk", request_id=request_id)
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

    def get_topics(self, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_topics() from files stored on disk", request_id=request_id)
        return contextualise(self.topics)

    def get_topic(self, topic_id: str, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_topic() from files stored on disk", request_id=request_id)
        topics = self.get_topics()
        if topics is None:
            return None
        return contextualise(
            next(
                (x for x in topics["topics"] if x["identifier"].endswith(topic_id)),
                None,
            )
        )

    def get_sub_topics(self, topic_id: str, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_sub_topics() from files stored on disk", request_id=request_id)
        topic = self.get_topic(topic_id)
        if topic is None:
            return None

        topics = self.get_topics()

        sub_topics = [
            x
            for x in topics["topics"]
            if len(x["parent_topics"]) > 0 and topic["@id"] in x["parent_topics"]
        ]

        if len(sub_topics) == 0:
            return None
        return contextualise(
            {
                "@id": f"https://staging.idpd.uk/topics/{topic_id}/subtopics",
                "@type": "hydra:Collection",
                "topics": sub_topics,
                "count": len(sub_topics),
                "offset": 0,
            }
        )

    def get_sub_topic(self, topic_id: str, sub_topic_id: str, request_id:Optional[str] = None) -> Dict:
        logger.info("Constructing get_sub_topic() from files stored on disk", request_id=request_id)
        raise NotImplementedError
