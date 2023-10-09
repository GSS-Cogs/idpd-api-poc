from abc import ABC, abstractmethod
from typing import Dict


class BaseMetadataStore(ABC):
    def __init__(self):
        self.setup()

    @abstractmethod
    def setup(self) -> Dict:
        """
        Runs any setup code required by a given implementation
        of a metadata store.
        """

    @abstractmethod
    def get_datasets(self) -> Dict:
        """
        Gets all datasets
        """

    @abstractmethod
    def get_dataset(self, dataset_id: str) -> Dict:
        """
        Gets a specific dataset
        """

    @abstractmethod
    def get_editions(self, dataset_id: str) -> Dict:
        """
        Gets all editions of a specific dataset
        """

    @abstractmethod
    def get_edition(self, dataset_id: str, edition_id: str) -> Dict:
        """
        Gets a specific edition of a specific dataset
        """

    @abstractmethod
    def get_versions(self, dataset_id: str, edition_id: str) -> Dict:
        """
        Gets all versions of a specific edition of a specific dataset
        """

    @abstractmethod
    def get_version(self, dataset_id: str, edition_id: str, version_id: str) -> Dict:
        """
        Gets a specific version of a specific edition of a specific dataset
        """

    @abstractmethod
    def get_publishers(self) -> Dict:
        """
        Gets all publishers
        """

    @abstractmethod
    def get_publisher(self, publisher_id: str) -> Dict:
        """
        Get a specific publisher
        """

    @abstractmethod
    def get_topics(self) -> Dict:
        """
        Get all topics
        """

    @abstractmethod
    def get_topic(self) -> Dict:
        """
        Get a specific topic
        """

    @abstractmethod
    def get_sub_topics(self, topic_id: str) -> Dict:
        """
        Get all sub-topics for a specific topic
        """

    @abstractmethod
    def get_sub_topic(self, topic_id: str, sub_topic_id: str) -> Dict:
        """
        Get a specific sub-topic for a specific topic
        """
