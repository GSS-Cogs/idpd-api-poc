from abc import ABC, abstractmethod


class BaseMetadataStore(ABC):
    def __init__(self):
        self.setup()

    @abstractmethod
    def setup(self):
        """ """

    @abstractmethod
    def get_datasets(self):
        """ """

    @abstractmethod
    def get_dataset(self):
        """ """

    @abstractmethod
    def get_editions(self):
        """ """

    @abstractmethod
    def get_edition(self):
        """ """

    @abstractmethod
    def get_publishers(self):
        """ """

    @abstractmethod
    def get_publisher(self):
        """ """

    @abstractmethod
    def get_topics(self):
        """ """

    @abstractmethod
    def get_topic(self):
        """ """