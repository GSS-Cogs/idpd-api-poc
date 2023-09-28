
from os import getcwd
import csv
import pytest

from store.stub.store import StubCsvStore


def test_get_version():
    """to test the get_csv does return csv"""


    test_intance = StubCsvStore()

    the_csv = csv.reader(test_intance.get_version("cipd", "2022-3","1"))




