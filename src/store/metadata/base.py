from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseMetadataStore(ABC):
    @abstractmethod
    def setup(self):
        """
        Runs any setup code required by a given implementation
        of a metadata store.
        """

    @abstractmethod
    def get_datasets(self) -> Optional[Dict]:
        """
        Gets all datasets
        """

    @abstractmethod
    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """
        Gets a specific dataset
        """

    @abstractmethod
    def get_editions(self, dataset_id: str) -> Optional[Dict]:
        """
        Gets all editions of a specific dataset
        """

    @abstractmethod
    def get_edition(self, dataset_id: str, edition_id: str) -> Optional[Dict]:
        """
        Gets a specific edition of a specific dataset
        """

    @abstractmethod
    def get_versions(self, dataset_id: str, edition_id: str) -> Optional[Dict]:
        """
        Gets all versions of a specific edition of a specific dataset
        """

    @abstractmethod
    def get_version(
        self, dataset_id: str, edition_id: str, version_id: str
    ) -> Optional[Dict]:
        """
        Gets a specific version of a specific edition of a specific dataset
        """

    @abstractmethod
    def get_publishers(self) -> Optional[Dict]:
        """
        Gets all publishers
        """

    @abstractmethod
    def get_publisher(self, publisher_id: str) -> Optional[Dict]:
        """
        Get a specific publisher
        """

    @abstractmethod
    def get_topics(self) -> Optional[Dict]:
        """
        Get all topics
        """

    @abstractmethod
    def get_topic(self) -> Optional[Dict]:
        """
        Get a specific topic
        """

    @abstractmethod
    def get_sub_topics(self, topic_id: str) -> Optional[Dict]:
        """
        Get all sub-topics for a specific topic
        """
