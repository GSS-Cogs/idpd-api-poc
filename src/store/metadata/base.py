from abc import ABC, abstractmethod

class BaseMetadataStore(ABC):

    # Every client runs the setup method
    def __init__(self):
        self.setup()

    # Every client must have a setup method
    @abstractmethod
    def setup(self):
        ...

    @abstractmethod
    def get_datasets(self):
        ...
