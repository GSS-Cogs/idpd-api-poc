from abc import ABC, abstractmethod


class BaseCsvStore(ABC):
    def __init__(self):
        self.setup()

    @abstractmethod
    def setup(self):
        """ """

    @abstractmethod
    def get_version(self, dataset_id: str, edition_id: str, version_id: str):
        """ """
