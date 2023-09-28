
from os import getcwd
import csv
import pathlib
import pytest
from pathlib import Path

from store.stub.store import StubMetadataStore


def test_get_csv():
    """to test the get_csv does return csv"""


    test_intance = StubMetadataStore()

    the_csv = csv.reader(test_intance.get_csv("dataset"))

    assert the_csv 




