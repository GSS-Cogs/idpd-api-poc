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
