from abc import ABC, abstractmethod
from sparql import run_sparql

class BaseStore(ABC):

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


class SparqlStore(BaseStore):

    # Do any setup this client requires
    def setup(self):
        # set the url for sparql
        self.url = # get it from an env var

    def get_datasets(self):
        # do stuff
        # use self.url or anything else you set in setup

        result = run_sparql(self.url)